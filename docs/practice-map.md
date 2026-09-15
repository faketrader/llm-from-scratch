# 书籍与实践索引

本表是项目维护索引，对应教材的42章及24个配套实验；它不进入教材。章节按概念依赖组织，实践按任务组织，二者为多对多关系；关联表示可用于学习或验证相关机制，不表示实验已经执行，也不要求把同一实践全文重复写入各章。


## 方向入口

| 方向 | 实践入口与深入主题 |
|---|---|
| 共同基础 | `10 → 20 → 21 → 30 → 31`，分别验证基础、数据、分词、Transformer 与生成 |
| 应用智能体系统 | `50 → 91 → 90`；提前阅读 `70` 的威胁模型与工具授权，Harness 深入结合教材智能体架构与运行系统 |
| 模型训练方法 | 训练知识 → `41` 的 SFT → `42`；预训练 `40`，数据 `A20`，对齐与推理 `41 → A30` |
| 训练推理系统 | 资源预算 `A10`；推理服务 `50 → 60 → 70 → A50`，训练系统 `40 → A40`，模型优化 `A60` |
| 共通方法与专题 | `50` 评估、`70` 安全；`E10` 模型审计与 `E20`、`E30`、`E40`、`E50` 模型专题 |

知识、资产和运行前置见[实践路线](../notebook/README.md)。主题选读需与完整实验执行范围区分，以下章节索引用于定位内容。

## 章节与实践

| 章节 | 关联实践 |
|---|---|
| [绪论](../book/textbook/chapters/11-introduction.tex) | 阅读路线与基础论述 |
| [数学基础](../book/textbook/chapters/12-probability-information.tex) | [10_foundations.ipynb](../notebook/10_foundations.ipynb)、[40_pre_training.ipynb](../notebook/40_pre_training.ipynb) |
| [神经网络基础](../book/textbook/chapters/13-tensors-autodiff.tex) | [10_foundations.ipynb](../notebook/10_foundations.ipynb) |
| [文本表示](../book/textbook/chapters/21-text-representation.tex) | [21_tokenizer.ipynb](../notebook/21_tokenizer.ipynb)、[31_nlp_gpt.ipynb](../notebook/31_nlp_gpt.ipynb)、[E30_nlp_bert.ipynb](../notebook/E30_nlp_bert.ipynb)、[30_transformer.ipynb](../notebook/30_transformer.ipynb) |
| [注意力机制](../book/textbook/chapters/22-attention.tex) | [30_transformer.ipynb](../notebook/30_transformer.ipynb)、[31_nlp_gpt.ipynb](../notebook/31_nlp_gpt.ipynb) |
| [Transformer 网络结构](../book/textbook/chapters/24-transformer.tex) | [30_transformer.ipynb](../notebook/30_transformer.ipynb) |
| [位置表示](../book/textbook/chapters/23-position-representation.tex) | [30_transformer.ipynb](../notebook/30_transformer.ipynb) |
| [自回归语言建模](../book/textbook/chapters/26-autoregressive-generation.tex) | [31_nlp_gpt.ipynb](../notebook/31_nlp_gpt.ipynb)、[30_transformer.ipynb](../notebook/30_transformer.ipynb) |
| [模型评估](../book/textbook/chapters/91-evaluation-statistics.tex) | [50_model_evaluation.ipynb](../notebook/50_model_evaluation.ipynb) |
| [模型安全](../book/textbook/chapters/92-model-application-security.tex) | [70_model_safety.ipynb](../notebook/70_model_safety.ipynb) |
| [上下文学习](../book/textbook/chapters/71-context-learning.tex) | [91_prompt_reasoning.ipynb](../notebook/91_prompt_reasoning.ipynb) |
| [信息检索](../book/textbook/chapters/72-information-retrieval.tex) | [90_llm_applications.ipynb](../notebook/90_llm_applications.ipynb) |
| [检索增强生成](../book/textbook/chapters/73-rag-systems.tex) | 阅读路线与基础论述 |
| [领域应用](../book/textbook/chapters/76-domain-applications.tex) | [90_llm_applications.ipynb](../notebook/90_llm_applications.ipynb)、[50_model_evaluation.ipynb](../notebook/50_model_evaluation.ipynb) |
| [智能体架构](../book/textbook/chapters/74-agent-architecture.tex) | [90_llm_applications.ipynb](../notebook/90_llm_applications.ipynb) |
| [智能体运行系统](../book/textbook/chapters/75-agent-runtime.tex) | [90_llm_applications.ipynb](../notebook/90_llm_applications.ipynb) |
| [优化及泛化](../book/textbook/chapters/14-optimization-generalization.tex) | [10_foundations.ipynb](../notebook/10_foundations.ipynb)、[40_pre_training.ipynb](../notebook/40_pre_training.ipynb) |
| [训练数据工程基础](../book/textbook/chapters/31-data-engineering.tex) | [20_dataset.ipynb](../notebook/20_dataset.ipynb)、[A20_data_engineering.ipynb](../notebook/A20_data_engineering.ipynb) |
| [训练稳定性](../book/textbook/chapters/34-training-stability.tex) | [40_pre_training.ipynb](../notebook/40_pre_training.ipynb)、[A40_training_optimization.ipynb](../notebook/A40_training_optimization.ipynb) |
| [监督微调](../book/textbook/chapters/41-supervised-finetuning.tex) | [41_post_training.ipynb](../notebook/41_post_training.ipynb)、[20_dataset.ipynb](../notebook/20_dataset.ipynb)、[A20_data_engineering.ipynb](../notebook/A20_data_engineering.ipynb) |
| [参数高效微调](../book/textbook/chapters/42-parameter-efficient-finetuning.tex) | [42_peft.ipynb](../notebook/42_peft.ipynb)、[A40_training_optimization.ipynb](../notebook/A40_training_optimization.ipynb) |
| [训练工程优化](../book/textbook/chapters/43-efficient-finetuning.tex) | [42_peft.ipynb](../notebook/42_peft.ipynb)、[A40_training_optimization.ipynb](../notebook/A40_training_optimization.ipynb) |
| [预训练原理](../book/textbook/chapters/33-pretraining-scaling.tex) | [40_pre_training.ipynb](../notebook/40_pre_training.ipynb)、[20_dataset.ipynb](../notebook/20_dataset.ipynb)、[A20_data_engineering.ipynb](../notebook/A20_data_engineering.ipynb)、[A10_resource_planning.ipynb](../notebook/A10_resource_planning.ipynb) |
| [强化学习基础](../book/textbook/chapters/44-reinforcement-learning.tex) | [41_post_training.ipynb](../notebook/41_post_training.ipynb)、[A30_reasoning_model.ipynb](../notebook/A30_reasoning_model.ipynb) |
| [人类反馈学习](../book/textbook/chapters/45-preference-alignment.tex) | [41_post_training.ipynb](../notebook/41_post_training.ipynb) |
| [可验证推理训练](../book/textbook/chapters/46-verifiable-reasoning.tex) | [41_post_training.ipynb](../notebook/41_post_training.ipynb)、[A30_reasoning_model.ipynb](../notebook/A30_reasoning_model.ipynb) |
| [模型规模及资源预算](../book/textbook/chapters/32-resource-budget.tex) | [A10_resource_planning.ipynb](../notebook/A10_resource_planning.ipynb) |
| [算力基础设施](../book/textbook/chapters/61-compute-infrastructure.tex) | [A10_resource_planning.ipynb](../notebook/A10_resource_planning.ipynb)、[A40_training_optimization.ipynb](../notebook/A40_training_optimization.ipynb)、[A50_inference_optimization.ipynb](../notebook/A50_inference_optimization.ipynb) |
| [分布式训练](../book/textbook/chapters/62-distributed-training.tex) | [A40_training_optimization.ipynb](../notebook/A40_training_optimization.ipynb)、[40_pre_training.ipynb](../notebook/40_pre_training.ipynb) |
| [增量解码](../book/textbook/chapters/51-incremental-decoding-cache.tex) | [A50_inference_optimization.ipynb](../notebook/A50_inference_optimization.ipynb)、[60_inference_deployment.ipynb](../notebook/60_inference_deployment.ipynb) |
| [批处理调度](../book/textbook/chapters/63-batching-scheduling.tex) | [60_inference_deployment.ipynb](../notebook/60_inference_deployment.ipynb)、[A50_inference_optimization.ipynb](../notebook/A50_inference_optimization.ipynb) |
| [模型服务架构](../book/textbook/chapters/64-serving-architecture.tex) | [60_inference_deployment.ipynb](../notebook/60_inference_deployment.ipynb)、[A50_inference_optimization.ipynb](../notebook/A50_inference_optimization.ipynb) |
| [推理计算优化](../book/textbook/chapters/52-inference-algorithms.tex) | [A50_inference_optimization.ipynb](../notebook/A50_inference_optimization.ipynb) |
| [模型优化](../book/textbook/chapters/53-model-optimization.tex) | [A60_model_compression.ipynb](../notebook/A60_model_compression.ipynb)、[A50_inference_optimization.ipynb](../notebook/A50_inference_optimization.ipynb) |
| [双向语言建模](../book/textbook/chapters/25-bidirectional-mlm.tex) | [E30_nlp_bert.ipynb](../notebook/E30_nlp_bert.ipynb) |
| [混合专家模型](../book/textbook/chapters/27-mixture-experts.tex) | [E10_open_model.ipynb](../notebook/E10_open_model.ipynb)、[A10_resource_planning.ipynb](../notebook/A10_resource_planning.ipynb)、[A40_training_optimization.ipynb](../notebook/A40_training_optimization.ipynb) |
| [长上下文建模](../book/textbook/chapters/28-long-context.tex) | [30_transformer.ipynb](../notebook/30_transformer.ipynb)、[A50_inference_optimization.ipynb](../notebook/A50_inference_optimization.ipynb)、[A10_resource_planning.ipynb](../notebook/A10_resource_planning.ipynb) |
| [开源模型体系](../book/textbook/chapters/29-open-models.tex) | [E10_open_model.ipynb](../notebook/E10_open_model.ipynb)、[A10_resource_planning.ipynb](../notebook/A10_resource_planning.ipynb) |
| [视觉 Transformer](../book/textbook/chapters/81-vision-transformer.tex) | [E40_cv_vit.ipynb](../notebook/E40_cv_vit.ipynb) |
| [多模态建模](../book/textbook/chapters/82-multimodal-alignment.tex) | [E20_multimodal_llm.ipynb](../notebook/E20_multimodal_llm.ipynb) |
| [扩散模型的概率原理](../book/textbook/chapters/83-diffusion-probability.tex) | [E50_cv_diffusion.ipynb](../notebook/E50_cv_diffusion.ipynb) |
| [条件视觉生成](../book/textbook/chapters/84-conditional-vision.tex) | [E50_cv_diffusion.ipynb](../notebook/E50_cv_diffusion.ipynb) |

## 框架实践

框架操作放在实验现有实验中，教材保留工程职责与取舍分析。以下内容为新增实验指导与配套入口，未执行训练、推理或压测。

| 路线 | 实验位置 | 教材落点 | 实践范围 |
|---|---|---|---|
| 微调与后训练 | [微调与后训练实验](../book/workbook/labs/08-42_peft.tex) | [监督微调](../book/textbook/chapters/41-supervised-finetuning.tex)、[参数高效微调](../book/textbook/chapters/42-parameter-efficient-finetuning.tex)、[训练工程优化](../book/textbook/chapters/43-efficient-finetuning.tex)，框架分析重点位于参数高效微调 | Transformers、PEFT、TRL完整链条；LLaMA-Factory、Axolotl迁移对照 |
| 分布式训练 | [分布式训练实验](../book/workbook/labs/17-A40_training_optimization.tex) | [算力基础设施](../book/textbook/chapters/61-compute-infrastructure.tex)与[分布式训练](../book/textbook/chapters/62-distributed-training.tex)，框架分析重点位于分布式训练 | DeepSpeed ZeRO-2运行与恢复；ZeRO-3、FSDP2、Megatron-LM迁移条件 |
| 推理部署 | [推理部署实验](../book/workbook/labs/10-60_inference_deployment.tex) | 推理与系统相关章节，重点见[模型服务架构](../book/textbook/chapters/64-serving-architecture.tex) | vLLM服务链条、SGLang迁移、压测与故障实验；TensorRT-LLM平台对照 |

训练入口：[train_adapter.py](../book/workbook/examples/train_adapter.py)。它使用预先准备的本地模型和JSONL数据，支持单卡LoRA、全参数训练及训练器管理的分布式后端；运行参数、EOS与数据契约见[微调与后训练实验](../book/workbook/labs/08-42_peft.tex)，分片和恢复见[分布式训练实验](../book/workbook/labs/17-A40_training_optimization.tex)。接口核查以相应版本的官方一手来源为准。
