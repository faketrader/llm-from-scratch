# LFS 全书规划（编写中）

五篇，共42章。[文本表示](../book/textbook/chapters/21-text-representation.tex)贯通文本输入与嵌入表示，随后按[注意力机制](../book/textbook/chapters/22-attention.tex)—[Transformer 网络结构](../book/textbook/chapters/24-transformer.tex)—[位置表示](../book/textbook/chapters/23-position-representation.tex)的概念依赖编排。

## 阅读路线：共同基础与三条方向

正文按知识依赖组织为五篇42章，阅读路线按学习目标组合章节。共同基础之后进入应用智能体系统、模型训练方法、训练推理系统三条方向；各方向分别设置入门主线和深入专题。方向之间按具体知识依赖衔接。

### 语言模型理论基础

入门前具备向量与矩阵运算、基础概率和微积分知识；实践另需 Python。共同基础以理解模型的一次输入、计算与输出为学习终点，按以下顺序选读：

| 顺序 | 阅读位置 | 必须掌握的范围 |
|---|---|---|
| 1 | [绪论](../book/textbook/chapters/11-introduction.tex) | 条件生成、模型与系统的职责、训练与推理的区别 |
| 2 | [概率与信息](../book/textbook/chapters/12-probability-information.tex)、[张量与自动微分](../book/textbook/chapters/13-tensors-autodiff.tex)、[优化及泛化](../book/textbook/chapters/14-optimization-generalization.tex) | 条件概率、交叉熵的含义、张量形状、参数更新、数据划分与泛化；完整求导随训练方向展开 |
| 3 | [文本表示](../book/textbook/chapters/21-text-representation.tex) | 分词、词元编号、嵌入、特殊词元与输入掩码 |
| 4 | [注意力](../book/textbook/chapters/22-attention.tex)、[Transformer](../book/textbook/chapters/24-transformer.tex)、[位置表示](../book/textbook/chapters/23-position-representation.tex) | 查询键值、因果可见性、顺序信息、残差与前馈网络的前向数据流 |
| 5 | [自回归生成](../book/textbook/chapters/26-autoregressive-generation.tex) | 下一词元分布、移位监督、采样、终止、事实性与概率的区别 |
| 6 | [评估](../book/textbook/chapters/91-evaluation-statistics.tex)、[安全](../book/textbook/chapters/92-model-application-security.tex) | 评估对象、独立测试集、失败样本、威胁模型与工具授权 |

表中范围属于主题选读，完成它表示具备方向入门基础。进入具体章节的推导时，应先补齐该推导使用的数学与机制前提。章内危险弯道标记继续表示相对于该章主线可延后的内容；路线选读范围与章内标记分别使用。

共同基础的自查终点：能够沿词元、张量、条件分布和生成决策解释一次请求，说明训练怎样改变参数，并提出可检验的效果指标及失败边界。

### 三条方向

| 方向 | 专项前置 | 入门主线 | 深入专题 | 学习终点 |
|---|---|---|---|---|
| 应用智能体系统 | 共同基础；信息检索章所需的相似度与排序知识随章补齐 | [上下文学习](../book/textbook/chapters/71-context-learning.tex) → [信息检索](../book/textbook/chapters/72-information-retrieval.tex) → [RAG](../book/textbook/chapters/73-rag-systems.tex) → [领域应用](../book/textbook/chapters/76-domain-applications.tex)，同步阅读评估与安全相关内容 | [智能体架构](../book/textbook/chapters/74-agent-architecture.tex) → [Agent 运行系统](../book/textbook/chapters/75-agent-runtime.tex)，深入 harness、持久化、权限与失败恢复；长上下文按任务选读 | 能从任务、证据与评价方法设计应用；深入后能解释工具执行、状态恢复与终止条件 |
| 模型训练方法 | 完整掌握概率、自动微分、优化及注意力反向传播；理解 Transformer 和自回归训练目标 | [数据工程](../book/textbook/chapters/31-data-engineering.tex) → [资源预算](../book/textbook/chapters/32-resource-budget.tex) → [训练稳定性](../book/textbook/chapters/34-training-stability.tex) → [监督微调](../book/textbook/chapters/41-supervised-finetuning.tex) → [参数高效微调](../book/textbook/chapters/42-parameter-efficient-finetuning.tex) → [训练工程优化](../book/textbook/chapters/43-efficient-finetuning.tex)，配合评估与安全 | 预训练专题：数据工程 → [预训练与规模定律](../book/textbook/chapters/33-pretraining-scaling.tex)；对齐专题：[强化学习](../book/textbook/chapters/44-reinforcement-learning.tex) → [人类反馈学习](../book/textbook/chapters/45-preference-alignment.tex) → [可验证推理训练](../book/textbook/chapters/46-verifiable-reasoning.tex) | 能说明数据、损失、可训练参数和资源预算的关系，设计适配方案，并用独立评估检验收益与退化 |
| 训练推理系统 | 共同基础；[资源预算](../book/textbook/chapters/32-resource-budget.tex)与[算力基础设施](../book/textbook/chapters/61-compute-infrastructure.tex) | 推理服务分支：[增量解码](../book/textbook/chapters/51-incremental-decoding-cache.tex) → [批处理与调度](../book/textbook/chapters/63-batching-scheduling.tex) → [模型服务](../book/textbook/chapters/64-serving-architecture.tex)；训练系统分支：训练目标、自动微分与训练稳定性 → [分布式训练](../book/textbook/chapters/62-distributed-training.tex) | [推理计算优化](../book/textbook/chapters/52-inference-algorithms.tex)、[模型优化](../book/textbook/chapters/53-model-optimization.tex)；训练侧深入并行策略、通信与恢复。蒸馏和量化感知训练须补齐训练前置 | 能建立容量与性能模型，区分估算和测量，解释调度、并行与恢复策略，并设计质量约束下的验证方案 |

训练推理系统的两个分支可分别进入。学习分布式训练需先理解训练计算与状态；研究偏好对齐需补齐强化学习；系统服务入门按自身依赖推进。

Harness 指智能体中模型之外的执行与控制系统，归属应用智能体系统的深入专题。该方向负责任务状态、工具行为与执行权限；训练推理系统方向负责模型计算、资源调度与服务可靠性。涉及执行隔离时，前者定义权限和恢复语义，后者提供所需的计算与隔离能力。

### 跨方向专题与实践衔接

- 数据：共同基础掌握划分与泄漏；应用侧关注知识来源和索引更新；模型侧关注训练数据与采样；系统侧关注存储和供给吞吐。
- 评估与安全：共同方法在基础中建立，各方向分别检验应用任务、模型行为和系统指标；详细统计推断与安全分析在对应章节研读。
- 模型专题：[双向编码](../book/textbook/chapters/25-bidirectional-mlm.tex)、[混合专家](../book/textbook/chapters/27-mixture-experts.tex)、[长上下文](../book/textbook/chapters/28-long-context.tex)、[开源模型体系](../book/textbook/chapters/29-open-models.tex)按目标选择，先掌握所用机制，再分析具体模型。
- 多模态：[视觉 Transformer](../book/textbook/chapters/81-vision-transformer.tex) → [多模态对齐](../book/textbook/chapters/82-multimodal-alignment.tex)服务理解任务；[扩散概率原理](../book/textbook/chapters/83-diffusion-probability.tex) → [条件视觉生成](../book/textbook/chapters/84-conditional-vision.tex)服务生成任务。扩散路线需补齐概率推导，条件视觉生成需补齐所用视觉架构；各方向按任务加入相应专题。

路线描述阅读目标。实践通过[章节—实验索引](practice-map.md)选择对应实验，并遵循每个 Notebook 的学习契约、资产与环境要求。Notebook 的方向与知识前置见[实践目录](../notebook/README.md)和各文件学习契约；主题选读不构成单元格可独立运行的保证。学习终点是能力验收要求，实际运行结果需另行验证。

## 重点主题的落点

| 重点 | 章节 |
|---|---|
| 数据工程 | [训练数据工程基础](../book/textbook/chapters/31-data-engineering.tex) |
| 强化学习 | [强化学习基础](../book/textbook/chapters/44-reinforcement-learning.tex)、[人类反馈学习](../book/textbook/chapters/45-preference-alignment.tex)、[可验证推理训练](../book/textbook/chapters/46-verifiable-reasoning.tex) |
| RAG | [信息检索](../book/textbook/chapters/72-information-retrieval.tex)、[检索增强生成](../book/textbook/chapters/73-rag-systems.tex) |
| Agent 应用开发 | [智能体运行系统](../book/textbook/chapters/75-agent-runtime.tex) |
| 分布式训练 | [分布式训练](../book/textbook/chapters/62-distributed-training.tex) |
| 开源大模型：Llama、Qwen、DeepSeek 等 | [开源大模型体系](../book/textbook/chapters/29-open-models.tex) |
| 智能体架构 | [智能体架构](../book/textbook/chapters/74-agent-architecture.tex) |
| 领域应用 | [领域应用](../book/textbook/chapters/76-domain-applications.tex) |
| 算力基础设施 | [算力基础设施](../book/textbook/chapters/61-compute-infrastructure.tex) |

## 参考依据

- [大语言模型：从理论到实践（LLM-TAP-v2）](../references/LLM-TAP-v2.pdf)：借鉴专题内部的机制分类，以及数据、分布式训练、强化学习、RAG、智能体与多模态的内容划分。
- [大语言模型（LLMBook）](../references/LLMBook.pdf)：借鉴预训练—微调对齐—使用—评估的主线，以及规模定律、架构细节、长上下文和偏好优化的推导深度。

两书用于目录与代表性章节的写法比较。模型与硬件版本案例在成稿时依据官方技术报告、模型卡和架构文档核实。

- [DeepSeek 官方资料入口](https://www.deepseek.com/en/transparency/)
- [Qwen 官方资料入口](https://qwen.ai/qwenchat)
- [GLM 官方资料入口](https://github.com/zai-org)

## 全书目录

### 语言模型理论基础

1. [绪论](../book/textbook/chapters/11-introduction.tex)
2. [数学基础](../book/textbook/chapters/12-probability-information.tex)
3. [神经网络基础](../book/textbook/chapters/13-tensors-autodiff.tex)
4. [文本表示](../book/textbook/chapters/21-text-representation.tex)
5. [注意力机制](../book/textbook/chapters/22-attention.tex)
6. [Transformer 网络结构](../book/textbook/chapters/24-transformer.tex)
7. [位置表示](../book/textbook/chapters/23-position-representation.tex)
8. [自回归语言建模](../book/textbook/chapters/26-autoregressive-generation.tex)
9. [模型评估](../book/textbook/chapters/91-evaluation-statistics.tex)
10. [模型安全](../book/textbook/chapters/92-model-application-security.tex)

### 应用智能体系统

11. [上下文学习](../book/textbook/chapters/71-context-learning.tex)
12. [信息检索](../book/textbook/chapters/72-information-retrieval.tex)
13. [检索增强生成](../book/textbook/chapters/73-rag-systems.tex)
14. [领域应用](../book/textbook/chapters/76-domain-applications.tex)
15. [智能体架构](../book/textbook/chapters/74-agent-architecture.tex)
16. [智能体运行系统](../book/textbook/chapters/75-agent-runtime.tex)

### 模型训练方法

17. [优化及泛化](../book/textbook/chapters/14-optimization-generalization.tex)
18. [训练数据工程基础](../book/textbook/chapters/31-data-engineering.tex)
19. [训练稳定性](../book/textbook/chapters/34-training-stability.tex)
20. [监督微调](../book/textbook/chapters/41-supervised-finetuning.tex)
21. [参数高效微调](../book/textbook/chapters/42-parameter-efficient-finetuning.tex)
22. [训练工程优化](../book/textbook/chapters/43-efficient-finetuning.tex)
23. [预训练原理](../book/textbook/chapters/33-pretraining-scaling.tex)
24. [强化学习基础](../book/textbook/chapters/44-reinforcement-learning.tex)
25. [人类反馈学习](../book/textbook/chapters/45-preference-alignment.tex)
26. [可验证推理训练](../book/textbook/chapters/46-verifiable-reasoning.tex)

### 训练推理系统

27. [模型规模及资源预算](../book/textbook/chapters/32-resource-budget.tex)
28. [算力基础设施](../book/textbook/chapters/61-compute-infrastructure.tex)
29. [分布式训练](../book/textbook/chapters/62-distributed-training.tex)
30. [增量解码](../book/textbook/chapters/51-incremental-decoding-cache.tex)
31. [批处理调度](../book/textbook/chapters/63-batching-scheduling.tex)
32. [模型服务架构](../book/textbook/chapters/64-serving-architecture.tex)
33. [推理计算优化](../book/textbook/chapters/52-inference-algorithms.tex)
34. [模型优化](../book/textbook/chapters/53-model-optimization.tex)

### 模型架构拓展

35. [双向语言建模](../book/textbook/chapters/25-bidirectional-mlm.tex)
36. [混合专家模型](../book/textbook/chapters/27-mixture-experts.tex)
37. [长上下文建模](../book/textbook/chapters/28-long-context.tex)
38. [开源模型体系](../book/textbook/chapters/29-open-models.tex)
39. [视觉 Transformer](../book/textbook/chapters/81-vision-transformer.tex)
40. [多模态建模](../book/textbook/chapters/82-multimodal-alignment.tex)
41. [扩散模型的概率原理](../book/textbook/chapters/83-diffusion-probability.tex)
42. [条件视觉生成](../book/textbook/chapters/84-conditional-vision.tex)

## 目录与章内范围

### 语言模型理论基础

**绪论**

- 语言建模问题
- 模型与系统的关系
- 全书知识依赖
- 理论与实践的分工

**数学基础**

- 向量、矩阵、线性变换与梯度
- 条件概率与链式分解
- 期望与最大似然
- 熵、交叉熵及 KL 散度
- 条件生成与最大似然的统一表述

- 条件生成与最大似然的统一表述：

**神经网络基础**

- 神经元、激活函数与损失函数
- Softmax、梯度下降与训练流程
- 张量形状与线性映射
- 矩阵求导与计算图
- 链式法则与完整反向传播
- 反向传播的逐步计算

- 反向传播的逐步计算：

**文本表示**

- 文本记录、训练样本与模型序列
- 从字符串到词元编号、掩码与批输入
- N-gram 与统计语言模型
- 词向量与前馈神经网络
- RNN 与 LSTM
- 字符、字节与子词
- BPE 与 WordPiece
- 可逆性与词表权衡
- 特殊词元协议
- Unigram 与分词器训练

- Unigram 与分词器训练：

- 独热与查表等价
- 嵌入参数与查表梯度
- 输入输出权重共享
- 嵌入空间与语义几何

**注意力机制**

- 加权汇总与缩放点积
- Softmax 与掩码
- 多头与交叉注意力
- 梯度与复杂度
- 排列等变性与解释边界
- 核心推导与图示

- 核心推导与图示：

**Transformer 网络结构**

- FFN、激活与门控
- 残差连接
- LayerNorm 及 RMSNorm
- Pre-LN 与 Post-LN
- 编码器—解码器
- 结构选择的机制比较

- 结构选择的机制比较：

**位置表示**

- 排列等变性与顺序信息
- 可学习绝对位置
- 正弦位置编码
- 旋转位置编码
- 位置方案的边界及一致性

**自回归语言建模**

- GPT 数据流与移位监督
- 教师强制
- 温度与截断采样
- 束搜索
- 终止与重复退化

**模型评估**

- 分类与生成指标
- 评审校准
- 置信区间与配对比较
- 切片与污染
- 在线实验及多目标决策
- 评估对象与证据分层
- 常用数据集及基准协议
- 模型发布评测

- 评估对象与证据分层：
- 常用数据集及基准协议：
- 模型发布评测：

**模型安全**

- 威胁模型与提示注入
- 数据及模型供应链
- 工具授权与隐私
- 纵深防御
- 事件响应

### 应用智能体系统

**上下文学习**

- 零样本与少样本
- 示例选择
- 分步生成与自一致性
- 候选选择
- 计算预算
- 提示设计与上下文学习的机制边界

- 提示设计与上下文学习的机制边界：

**信息检索**

- 文档与索引
- BM25
- 稠密和混合检索
- 检索理论与表示学习
- 语料组织与检索评估

- 检索理论与表示学习：
- 语料组织与检索评估：

**检索增强生成**

- 重排与证据组装
- 引用与拒答
- 模块化 RAG 架构与优化
- RAG 系统的完整设计

- 模块化 RAG 架构与优化：
- RAG 系统的完整设计：

**领域应用**

- 领域应用的方法论
- 知识及文档密集型应用
- 业务流程及工业应用
- 专业服务及研发应用
- 应用架构与效果验证

- 领域应用的方法论：
- 知识及文档密集型应用：
- 业务流程及工业应用：
- 专业服务及研发应用：
- 应用架构与效果验证：

**智能体架构**

- 结构化动作与外部执行器
- 状态机与工作流
- ReAct 与记忆
- 权限与幂等
- 终止
- 智能体的感知、规划、记忆与行动
- 架构模式与设计取舍
- Harness 执行控制体系

- 智能体的感知、规划、记忆与行动：
- 架构模式与设计取舍：

**智能体运行系统**

- 应用分析与协议设计
- 执行引擎与持久化
- 工具接入与权限
- 测试、观测与上线
- 完整应用贯穿案例
- 编码 Harness 及个人智能体平台
- Computer Use 的观察及行动闭环
- 浏览器控制协议及适配

- 应用分析与协议设计：
- 执行引擎与持久化：
- 工具接入与权限：
- 测试、观测与上线：
- 完整应用贯穿案例：

### 模型训练方法

**优化及泛化**

- 梯度下降与随机优化
- 初始化与正则化
- 偏差与方差
- 数据泄漏及分布漂移

**训练数据工程基础**

- 样本与总体
- 独立性及分组、时间划分
- 数据模式与确定性变换
- 数据版本
- 数据分类与来源
- 清洗与质量筛选
- 精确与近似去重
- 污染与混合采样
- 分片
- 数据治理与可复现处理链
- 数据生产流水线
- 数据质量与采样机制

- 数据治理与可复现处理链：
- 数据生产流水线：
- 数据质量与采样机制：

**训练稳定性**

- Adam 与 AdamW 推导
- 学习率日程
- 梯度裁剪与随机状态
- 检查点及恢复一致性
- 数值稳定性与训练诊断

- 数值稳定性与训练诊断：

**监督微调**

- 后训练数据类型与生产接口
- 条件监督与多轮对话
- 回答掩码与模板
- 样本权重
- 能力迁移与遗忘
- 指令数据构建与质量控制

- 指令数据构建与质量控制：

**参数高效微调**

- LoRA 低秩假设
- 参数量与梯度
- 初始化与模块选择
- 合并
- QLoRA 及其他适配方法
- 适配方法比较与低秩更新推导

- 适配方法比较与低秩更新推导：

**训练工程优化**

- 显存预算及可训练集合
- 有效监督词元及梯度累积
- 序列长度及数据装箱
- 混合精度及激活重计算
- 分布式微调方案的选用
- 微调执行评估

**预训练原理**

- 训练分布与下一词元目标
- 文档边界与装箱
- 损失归一化与困惑度
- 训练预算
- 规模定律与计算预算分配
- 预训练任务与数据配比

- 规模定律与计算预算分配：
- 预训练任务与数据配比：

**强化学习基础**

- 状态、动作、轨迹、回报与策略的符号约定
- 对数导数技巧与 REINFORCE 推导
- 基线、优势函数与广义优势估计
- 重要性采样与 PPO 裁剪目标的动机
- 序列生成作为决策过程
- 策略训练的数据流
- 强化学习的理论基础

- 序列生成作为决策过程：
- 策略训练的数据流：
- 强化学习的理论基础：

**人类反馈学习**

- 奖励建模与 KL 正则化
- 基于人类反馈的强化学习（RLHF）
- DPO 推导
- GRPO
- 训练方法的结构比较
- KL 正则化目标—最优策略—偏好似然—DPO 损失
- GRPO 的组内优势与奖励方差问题

- 训练方法的结构比较：

**可验证推理训练**

- 结果及过程监督
- 验证器与拒绝采样
- 奖励利用
- 推理蒸馏
- 测试时计算
- 训练时与测试时的推理能力提升
- 面向工具任务的强化学习

- 训练时与测试时的推理能力提升：
- 面向工具任务的强化学习：

### 训练推理系统

**模型规模及资源预算**

- 参数计数与 FLOPs
- 权重、激活与训练状态
- KV 容量
- 带宽与计算瓶颈
- 可核算的资源模型

- 可核算的资源模型：

**算力基础设施**

- GPU 与加速器计算结构
- 主机、内存与单机互连
- 集群网络与集合通信
- 存储系统及数据通路
- 训练与推理的基础设施架构
- 资源管理与运行环境
- 可靠性、供电及散热
- 性能模型与容量规划
- 性能测量及容量推导
- 架构图与推导要求

- GPU 与加速器计算结构：
- 主机、内存与单机互连：
- 集群网络与集合通信：
- 存储系统及数据通路：
- 训练与推理的基础设施架构：
- 资源管理与运行环境：
- 可靠性、供电及散热：
- 性能模型与容量规划：
- 性能测量及容量推导：
- 架构图与推导要求：

**分布式训练**

- 词元加权累积
- 混合精度及激活重计算
- 数据并行
- ZeRO 与 FSDP
- 张量及流水并行
- 并行训练的通信与资源模型
- 分布式系统与训练通信

- 并行训练的通信与资源模型：
- 分布式系统与训练通信：

**增量解码**

- Prefill 与 Decode
- KV 推导
- MHA、GQA 与 MQA
- 前缀缓存与分页管理
- 缓存一致性
- 注意力结构与缓存容量比较

- 注意力结构与缓存容量比较：

**批处理调度**

- 静态与连续批处理
- 长度分桶与分块预填充
- 准入与背压
- 公平性
- 尾延迟

**模型服务架构**

- 制品、网关与路由
- 工作进程
- 流式协议与取消
- 发布回滚与故障恢复
- 遥测

**推理计算优化**

- 在线 Softmax
- FlashAttention
- 算子融合
- 编译与形状
- 精确推测解码及收益条件
- 长序列与解码优化的正确性

- 长序列与解码优化的正确性：

**模型优化**

- 数值表示、尺度与零点
- 误差与校准
- 离群值
- 量化方法与 QAT
- 低比特执行
- 量化误差与执行机制
- 结构化与非结构化稀疏
- SVD 与输入加权误差
- 分布和隐藏状态蒸馏
- 组合压缩
- 压缩方法的统一比较

- 量化误差与执行机制：
- 压缩方法的统一比较：

### 模型架构拓展

**双向语言建模**

- 双向表示与三类嵌入
- MLM 与 NSP
- 任务头
- 与自回归目标的区别

**混合专家模型**

- MoE 路由与专家负载
- 总参数与激活参数
- 专家混合的结构与训练机制

- 专家混合的结构与训练机制：

**长上下文建模**

- 相对位置与长上下文扩展
- 长序列注意力结构
- 长上下文训练
- 长距离能力评估
- 推导与结构图

- 相对位置与长上下文扩展：
- 长序列注意力结构：
- 长上下文训练：
- 长距离能力评估：
- 推导与结构图：

**开源模型体系**

- 开源程度与许可分层
- Llama 与 Mistral 模型系列
- DeepSeek 模型系列
- Qwen 模型系列
- GLM 模型系列
- 其他开源模型的扩展研究
- 模型选型、适配与验证
- 技术报告阅读与架构图

- 开源程度与许可分层：
- Llama 与 Mistral 模型系列：
- DeepSeek 模型系列：
- Qwen 模型系列：
- GLM 模型系列：
- 其他开源模型的扩展研究：
- 模型选型、适配与验证：
- 技术报告阅读与架构图：

**视觉 Transformer**

- 补丁表示与卷积等价性
- 二维位置
- 视觉编码
- 分辨率与计算权衡

**多模态建模**

- 视觉编码器
- 投影与重采样
- 融合架构
- 监督区域及分阶段训练
- 音视频时序
- 跨模态对齐与训练目标

- 跨模态对齐与训练目标：

**扩散模型的概率原理**

- 前向过程
- 反向后验
- 变分下界
- 噪声预测
- 时间参数化及采样
- 核心概率推导与过程图

- 核心概率推导与过程图：

**条件视觉生成**

- U-Net 与 Transformer 主干
- 文本条件与 CFG
- VAE 与潜空间
- 流匹配
- 视频扩展

## 编写与审核要求

核心定义、必要假设、符号说明及公式推导置于正文；术语、历史和次要限定使用页下注，按章编号。书内结构图与流程图采用TikZ，测量曲线来自真实数据。实践主题与章节多对多对应，不搬用Notebook单元组织。领域案例须有需求、数据、系统架构、评价和失败边界，不虚构实验结果。

资源预算章解释工作负载需求，算力章解释基础设施供给与瓶颈，分布式训练章解释算法与通信执行，三者各有侧重。算力算例明确假设，不将估算当作实测。


## 中英文术语索引

书末设置中文术语索引和英文术语索引，只列术语及其页码，与书前数学符号表分开。中文按拼音排序，英文按英文名称的字母顺序排序；随正文持续维护译名与首次定义位置。

## 参考答案

习题按章号与题号汇集习题参考解析，计算与推导给出必要条件、关键步骤及结果，开放题给出合理方案和边界。教材教学例题在正文中给出完整推导；习题题号链接至解析，解析中的题号链接至习题。

## 阅读标记

- 仅设必修与选修（可暂时跳过）两级，以知识依赖而非篇幅或表面难度划分。
- 节首外侧页边标示选修，教材例题与习题逐题标示选修，解析与原题一致。
- 核心定义、必要推导和基础算例为必修；可独立移开的扩展证明与专题为选修。
- 仅选修在外侧页边显示危险弯道图标（manfnt），不附文字；必修不显示标记、不预留标记间距。阅读说明解释一次图例；后续主线不依赖未交代的选修前提。

## 两册分工

教材保留42章理论、必要推导、教学例题、术语索引与参考文献，不引用习题或实验。习题以《习题解析与实验指导》为书名，按“习题—24个实验指导—参考解析—参考文献”四个独立部分编排，允许引用教材。习题编排504道习题及其504份参考解析；习题不引用文献，第四部分仅列实验指导实际引用的论文与框架资料。源文件与实验落点见workbook-map.json。
