#!/usr/bin/env python3
"""为 Notebook 中可静态确定的矩阵和高阶张量补充固定形状注释。"""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TENSOR_CONSTRUCTORS = {
    "torch.empty",
    "torch.full",
    "torch.ones",
    "torch.rand",
    "torch.randn",
    "torch.zeros",
    "np.empty",
    "np.full",
    "np.ones",
    "np.random.rand",
    "np.random.randn",
    "np.zeros",
    "numpy.empty",
    "numpy.full",
    "numpy.ones",
    "numpy.random.rand",
    "numpy.random.randn",
    "numpy.zeros",
}


@dataclass(frozen=True)
class Annotation:
    """描述一条需要紧邻赋值语句插入的固定形状注释。"""

    lineno: int
    target: str
    descriptions: tuple[str, ...]


def qualified_name(node: ast.AST) -> str:
    """返回 Name/Attribute 调用目标的点分名称。"""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = qualified_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def static_value(node: ast.AST, constants: dict[str, Any]) -> Any | None:
    """在不执行代码的前提下求值简单整数和整数形状表达式。"""
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    if isinstance(node, ast.Name):
        return constants.get(node.id)
    if isinstance(node, (ast.Tuple, ast.List)):
        values = [static_value(item, constants) for item in node.elts]
        return values if all(value is not None for value in values) else None
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        value = static_value(node.operand, constants)
        return -value if isinstance(value, int) else None
    if isinstance(node, ast.BinOp):
        left = static_value(node.left, constants)
        right = static_value(node.right, constants)
        if not isinstance(left, int) or not isinstance(right, int):
            return None
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.FloorDiv) and right != 0:
            return left // right
        if isinstance(node.op, ast.Pow) and right >= 0:
            return left**right
    return None


def nested_literal_shape(node: ast.AST) -> list[int] | None:
    """推导规则嵌套 list/tuple 字面量的形状。"""
    if not isinstance(node, (ast.List, ast.Tuple)):
        return []
    if not node.elts:
        return [0]
    child_shapes = [nested_literal_shape(child) for child in node.elts]
    if any(shape is None for shape in child_shapes):
        return None
    if not all(shape == child_shapes[0] for shape in child_shapes):
        return None
    return [len(node.elts), *child_shapes[0]]


def positive_fixed_shape(value: Any) -> list[int] | None:
    """仅接受至少二维且所有轴均为正整数的固定形状。"""
    if not isinstance(value, list) or len(value) < 2:
        return None
    if not all(isinstance(dim, int) and dim > 0 for dim in value):
        return None
    return value


def call_arguments(call: ast.Call, constants: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
    """静态解析调用的位置参数与关键字参数。"""
    args = [static_value(arg, constants) for arg in call.args]
    kwargs = {
        keyword.arg: static_value(keyword.value, constants)
        for keyword in call.keywords
        if keyword.arg is not None
    }
    return args, kwargs


def format_shape(shape: list[int]) -> str:
    """使用课程统一的方括号格式呈现形状。"""
    return "[" + ", ".join(str(dim) for dim in shape) + "]"


def infer_call_descriptions(
    target: str, call: ast.Call, constants: dict[str, Any]
) -> tuple[str, ...]:
    """推导赋值右侧调用产生的固定张量或模块参数形状。"""
    if (
        isinstance(call.func, ast.Attribute)
        and call.func.attr
        in {"cpu", "cuda", "eval", "requires_grad_", "to", "train"}
        and isinstance(call.func.value, ast.Call)
    ):
        return infer_call_descriptions(target, call.func.value, constants)

    function = qualified_name(call.func)
    args, kwargs = call_arguments(call, constants)

    if function in TENSOR_CONSTRUCTORS:
        shape_value = args[:1] if function.endswith("full") else args
        if len(shape_value) == 1 and isinstance(shape_value[0], list):
            shape_value = shape_value[0]
        shape = positive_fixed_shape(shape_value)
        return (f"{target}.shape = {format_shape(shape)}",) if shape else ()

    if function in {"torch.randint", "np.random.randint", "numpy.random.randint"}:
        size = kwargs.get("size")
        if size is None:
            size = args[2] if len(args) >= 3 else args[1] if len(args) >= 2 else None
        shape = positive_fixed_shape(size)
        return (f"{target}.shape = {format_shape(shape)}",) if shape else ()

    if function in {"torch.tensor", "torch.as_tensor", "np.array", "numpy.array"} and call.args:
        shape = positive_fixed_shape(nested_literal_shape(call.args[0]))
        return (f"{target}.shape = {format_shape(shape)}",) if shape else ()

    if function in {"torch.eye", "np.eye", "numpy.eye"} and args:
        rows = args[0]
        columns = args[1] if len(args) > 1 else rows
        shape = positive_fixed_shape([rows, columns])
        return (f"{target}.shape = {format_shape(shape)}",) if shape else ()

    if function in {"nn.Linear", "torch.nn.Linear"}:
        in_features = args[0] if args else kwargs.get("in_features")
        out_features = args[1] if len(args) > 1 else kwargs.get("out_features")
        shape = positive_fixed_shape([out_features, in_features])
        if shape:
            return (
                f"{target}.weight.shape = {format_shape(shape)}（out_features, in_features）",
            )

    if function in {"nn.Embedding", "torch.nn.Embedding"}:
        num_embeddings = args[0] if args else kwargs.get("num_embeddings")
        embedding_dim = args[1] if len(args) > 1 else kwargs.get("embedding_dim")
        shape = positive_fixed_shape([num_embeddings, embedding_dim])
        if shape:
            return (
                f"{target}.weight.shape = {format_shape(shape)}（num_embeddings, embedding_dim）",
            )

    if function in {"nn.MultiheadAttention", "torch.nn.MultiheadAttention"}:
        embed_dim = args[0] if args else kwargs.get("embed_dim")
        if isinstance(embed_dim, int) and embed_dim > 0:
            return (
                f"{target}.in_proj_weight.shape = {format_shape([3 * embed_dim, embed_dim])}",
                f"{target}.out_proj.weight.shape = {format_shape([embed_dim, embed_dim])}",
            )

    if function in {"nn.Conv1d", "torch.nn.Conv1d", "nn.Conv2d", "torch.nn.Conv2d"}:
        in_channels = args[0] if args else kwargs.get("in_channels")
        out_channels = args[1] if len(args) > 1 else kwargs.get("out_channels")
        kernel = args[2] if len(args) > 2 else kwargs.get("kernel_size")
        groups = kwargs.get("groups", 1)
        if isinstance(kernel, int):
            kernel_shape = [kernel] if function.endswith("Conv1d") else [kernel, kernel]
        elif isinstance(kernel, list):
            kernel_shape = kernel
        else:
            kernel_shape = []
        if (
            isinstance(in_channels, int)
            and isinstance(out_channels, int)
            and isinstance(groups, int)
            and groups > 0
            and in_channels % groups == 0
            and kernel_shape
        ):
            shape = positive_fixed_shape(
                [out_channels, in_channels // groups, *kernel_shape]
            )
            if shape:
                return (
                    f"{target}.weight.shape = {format_shape(shape)}（out_channels, in_channels/groups, kernel）",
                )

    if isinstance(call.func, ast.Attribute) and call.func.attr in {"reshape", "view"}:
        shape_value = args[0] if len(args) == 1 and isinstance(args[0], list) else args
        shape = positive_fixed_shape(shape_value)
        return (f"{target}.shape = {format_shape(shape)}",) if shape else ()

    if function in {"nn.Sequential", "torch.nn.Sequential"}:
        descriptions: list[str] = []
        for index, child in enumerate(call.args):
            if isinstance(child, ast.Call):
                descriptions.extend(
                    infer_call_descriptions(f"{target}[{index}]", child, constants)
                )
        return tuple(descriptions)

    if function in {"nn.Parameter", "torch.nn.Parameter"} and call.args:
        inner = call.args[0]
        if isinstance(inner, ast.Call):
            descriptions = infer_call_descriptions(target, inner, constants)
            return tuple(
                description.replace(f"{target}.shape", f"{target}.shape", 1)
                for description in descriptions
            )

    return ()


def target_name(node: ast.AST) -> str | None:
    """返回可读的简单赋值目标名称。"""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return qualified_name(node)
    return None


def collect_annotations(source: str, constants: dict[str, Any]) -> list[Annotation]:
    """收集一个代码单元内可静态证明的形状。"""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    annotations: list[Annotation] = []
    top_level_nodes = set(tree.body)
    assignments = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.Assign, ast.AnnAssign))
    ]
    assignments.sort(key=lambda node: (node.lineno, node.col_offset))

    for node in assignments:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        value = node.value
        if len(targets) != 1:
            continue
        name = target_name(targets[0])
        if name is None:
            continue

        if node in top_level_nodes and isinstance(targets[0], ast.Name):
            constant = static_value(value, constants)
            if constant is not None:
                constants[targets[0].id] = constant

        if not isinstance(value, ast.Call):
            continue
        descriptions = infer_call_descriptions(name, value, constants)
        if descriptions:
            annotations.append(Annotation(node.lineno, name, descriptions))
    return annotations


def annotation_comment(annotation: Annotation, indent: str) -> str:
    """生成单行中文固定形状注释。"""
    return f"{indent}# 固定形状：{'；'.join(annotation.descriptions)}。\n"


def annotate_source(source: str, constants: dict[str, Any]) -> tuple[str, int, list[str]]:
    """为一个代码单元插入缺失注释并返回修改后的源码。"""
    annotations = collect_annotations(source, constants)
    lines = source.splitlines(keepends=True)
    inserted = 0
    missing_descriptions: list[str] = []

    for annotation in sorted(annotations, key=lambda item: item.lineno, reverse=True):
        index = annotation.lineno - 1
        nearby = "".join(lines[max(0, index - 2) : index])
        marker = f"# 固定形状：{';'.join(annotation.descriptions)}"
        normalized_nearby = nearby.replace("；", ";")
        if marker in normalized_nearby:
            continue
        if index >= len(lines):
            missing_descriptions.extend(annotation.descriptions)
            continue
        indent = lines[index][: len(lines[index]) - len(lines[index].lstrip())]
        lines.insert(index, annotation_comment(annotation, indent))
        inserted += 1

    return "".join(lines), inserted, missing_descriptions


def notebook_paths(root: Path, explicit_paths: list[str]) -> list[Path]:
    """解析待检查的 Notebook 路径。"""
    if explicit_paths:
        return sorted(Path(path) for path in explicit_paths)
    return sorted(root.glob("*.ipynb"))


def process_notebook(path: Path, write: bool) -> tuple[int, int, list[str]]:
    """检查或更新单个 Notebook，返回候选、缺失与错误摘要。"""
    notebook = json.loads(path.read_text(encoding="utf-8"))
    constants: dict[str, Any] = {}
    changed = 0
    errors: list[str] = []

    for cell_index, cell in enumerate(notebook.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        updated, inserted, cell_errors = annotate_source(source, constants)
        if inserted:
            changed += inserted
            if write:
                cell["source"] = updated.splitlines(keepends=True)
        errors.extend(f"cell={cell_index}: {message}" for message in cell_errors)

    if write and changed:
        path.write_text(
            json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )
    return changed, len(notebook.get("cells", [])), errors


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="可选的 Notebook 路径；默认扫描当前目录")
    default_root = (
        Path.cwd()
        if any(Path.cwd().glob("*.ipynb"))
        else Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--root", type=Path, default=default_root, help="Notebook 根目录")
    parser.add_argument("--write", action="store_true", help="写入缺失的固定形状注释")
    return parser.parse_args()


def main() -> int:
    """执行全树固定形状检查或写入。"""
    args = parse_args()
    paths = notebook_paths(args.root, args.paths)
    total_changes = 0
    total_cells = 0
    errors: list[str] = []

    for path in paths:
        changes, cells, notebook_errors = process_notebook(path, args.write)
        total_changes += changes
        total_cells += cells
        errors.extend(f"{path.name}: {message}" for message in notebook_errors)
        if changes:
            action = "inserted" if args.write else "missing"
            print(f"{path.name}: {action}={changes}")

    print(
        f"FIXED_SHAPE_AUDIT notebooks={len(paths)} cells={total_cells} "
        f"changes={total_changes} mode={'write' if args.write else 'check'}"
    )
    if errors:
        print("\n".join(errors))
        return 2
    if total_changes and not args.write:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
