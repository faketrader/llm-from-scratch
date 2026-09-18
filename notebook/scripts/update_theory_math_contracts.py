#!/usr/bin/env python3
"""为全部课程 Notebook 补充“语言说明 + 数学表示 + 符号与边界”契约。

脚本只插入或更新带固定标记的 Markdown 单元，不执行 Notebook，不改动代码单元、
执行计数和输出。重复运行是幂等的，便于后续统一维护课程写作标准。
"""

from __future__ import annotations

import re
from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]
MARKER = "<!-- theory-math-contract:v1 -->"


CONTENT: dict[str, str] = {
    "10_foundations.ipynb": r"""监督学习不是记住训练样本，而是在给定数据分布上寻找能够降低期望风险的参数。有限训练集只能给出经验风险，因此还需要独立验证集估计泛化误差：

$$
\hat{R}_{\mathrm{train}}(\theta)=\frac{1}{N}\sum_{i=1}^{N}\ell\!\left(f_\theta(x_i),y_i\right),\qquad
\theta_{t+1}=\theta_t-\eta\nabla_\theta\hat{R}_{\mathrm{train}}(\theta_t)
$$

其中，$x_i\in\mathbb{R}^{D}$ 是第 $i$ 个输入，$y_i$ 是目标，$f_\theta$ 是参数为 $\theta$ 的模型，$\ell$ 是单样本损失，$N$ 是训练样本数，$\eta$ 是学习率。代码中的 `loss` 对应 $\hat R$，`parameter.grad` 对应梯度；PyTorch 的优化器负责参数更新。经验风险下降只说明训练目标得到优化，不等价于验证风险或真实业务风险同步下降。""",
    "20_dataset.ipynb": r"""数据划分的核心不是“按比例切几份”，而是让同一原子样本或同一泄漏组稳定地只属于一个集合。可将规范化后的分组键 $g(x)$ 哈希到 $M$ 个桶：

$$
b(x)=\operatorname{int}\!\left(H(g(x))[:k],16\right)\bmod M,
\qquad
D_{\mathrm{train}}\cap D_{\mathrm{valid}}=D_{\mathrm{train}}\cap D_{\mathrm{test}}=\varnothing
$$

其中，$H$ 是固定版本的内容哈希，$g(x)$ 是样本、会话、文档或问题家族的稳定分组键，$b(x)$ 是桶编号，$M$ 是桶总数。`stable_split` 对应 $b(x)$，`DatasetDict` 承载三个互斥集合。公式保证的是给定规范化、分组键和哈希算法下的确定性；如果清洗规则或分组粒度变化，划分成员也会变化，必须生成新的数据版本。""",
    "21_tokenizer.ipynb": r"""Tokenizer 把字符串映射为有限词表中的整数序列，再把整数序列恢复为字节或文本。BPE 每轮选择当前语料中频次最高的相邻符号对并合并：

$$
T:\mathcal{S}\rightarrow\{0,\ldots,V-1\}^{L},\qquad
(a^*,b^*)=\arg\max_{(a,b)}\operatorname{count}_{\mathcal C}(a,b)
$$

其中，$\mathcal S$ 是输入字符串集合，$V$ 是词表大小，$L$ 是编码后的 Token 数，$\mathcal C$ 是当前分词后的训练语料。代码中的 `vocab` 对应大小为 $V$ 的 ID 空间，`merges` 对应有序合并规则。Token ID 只是词表行索引，不表示语义距离；模型输入还需通过 Embedding 查表变为 $[B,L,D]$ 的稠密向量。""",
    "30_transformer.ipynb": r"""Attention 先用查询与键计算相关性，再把归一化权重用于值向量的加权聚合。缩放项抑制维度增大造成的点积方差：

$$
Q=XW_Q,\quad K=XW_K,\quad V=XW_V,\qquad
\operatorname{Attention}(Q,K,V)=\operatorname{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}+M\right)V
$$

其中，$X\in\mathbb{R}^{B\times L\times d_{\mathrm{model}}}$，$Q,K\in\mathbb{R}^{B\times H\times L\times d_k}$，$V\in\mathbb{R}^{B\times H\times L\times d_v}$，$M$ 是可广播的 Mask。标准多头实现通常要求 $d_{\mathrm{model}}\bmod H=0$，从而每头维度 $d_k=d_{\mathrm{model}}/H$。`my_scaled_dot_product_attention` 对应公式主体，`torch.nn.functional.scaled_dot_product_attention` 对应生产接口；FlashAttention 等 Kernel 改变访存与数值路径，不改变上述数学语义。""",
    "31_nlp_gpt.ipynb": r"""Decoder-only 模型把序列联合概率分解为一系列条件概率，并用因果 Mask 禁止位置 $t$ 读取未来 Token：

$$
p(x_{1:L})=\prod_{t=1}^{L}p(x_t\mid x_{<t}),\qquad
M_{t,s}=\begin{cases}0,&s\le t\\-\infty,&s>t\end{cases}
$$

其中，$x_t$ 是位置 $t$ 的 Token，$L$ 是序列长度，$M\in\mathbb{R}^{L\times L}$。训练时 Logits 为 $[B,L,V]$，目标是右移后的 $[B,L]$ Token ID。`MyCausalSelfAttention` 对应因果可见性与 Attention 聚合，`CrossEntropyLoss` 对应条件负对数似然。对于多头注意力，查询头数 $N_q$ 与隐藏维度需满足实现的分头约束；GQA 还区分查询头 $N_q$ 和 KV 头 $N_{kv}$。头数关系描述网络结构，是否能按张量并行切分则取决于具体 Runtime 是否支持 KV 头复制。""",
    "40_pre_training.ipynb": r"""因果语言模型通过最小化有效 Token 上的负对数似然学习 Next-token 条件分布：

$$
\mathcal L_{\mathrm{CLM}}=-\frac{1}{N_{\mathrm{valid}}}
\sum_{b=1}^{B}\sum_{t=1}^{L-1}m_{b,t}\log p_\theta(x_{b,t+1}\mid x_{b,\le t}),
\qquad N_{\mathrm{valid}}=\sum_{b,t}m_{b,t}
$$

其中，$B$ 是 Micro-batch 大小，$L$ 是块长度，$m_{b,t}\in\{0,1\}$ 标记参与损失的 Token，$p_\theta$ 来自 $[B,L,V]$ Logits 的 Softmax。代码中的 `labels == -100` 对应 $m=0$；`CrossEntropyLoss` 实现 Log-Softmax 与负对数似然。Loss 只在固定 Tokenizer、数据版本、Mask 与 Reduction 口径下可比较。""",
    "41_post_training.ipynb": r"""后训练方法改变监督信号，但都需要明确样本单位和归约口径。SFT 只对回答区域计算 Token 损失；DPO 比较策略相对参考模型对优选与拒选回答的对数概率差：

$$
\mathcal L_{\mathrm{SFT}}=-\frac{1}{\sum m_t}\sum_t m_t\log\pi_\theta(y_t\mid x,y_{<t})
$$

$$
\mathcal L_{\mathrm{DPO}}=-\log\sigma\!\left(\beta\left[\log\frac{\pi_\theta(y^+\mid x)}{\pi_{\mathrm{ref}}(y^+\mid x)}-\log\frac{\pi_\theta(y^-\mid x)}{\pi_{\mathrm{ref}}(y^-\mid x)}\right]\right)
$$

其中，$m_t$ 是回答区 Label Mask，$y^+,y^-$ 是偏好对，$\beta$ 控制偏好间隔尺度。`completion_mask`、序列 Log-probability 与 TRL 的 `SFTTrainer`/`DPOTrainer` 分别对应这些对象。公式不消除数据偏差；错误偏好、长度偏差和奖励投机仍需切片评测。""",
    "42_peft.ipynb": r"""LoRA 冻结基座权重 $W$，用两个低秩矩阵表示任务增量，从而只训练较少参数：

$$
W'=W+\Delta W,\qquad
\Delta W=\frac{\alpha}{r}BA,qquad
A\in\mathbb{R}^{r\times d_{\mathrm{in}}},\;B\in\mathbb{R}^{d_{\mathrm{out}}\times r}
$$

其中，$W\in\mathbb{R}^{d_{\mathrm{out}}\times d_{\mathrm{in}}}$，$r$ 是秩，$\alpha$ 是缩放系数。单个线性层新增参数量为 $r(d_{\mathrm{in}}+d_{\mathrm{out}})$，而不是 $d_{\mathrm{in}}d_{\mathrm{out}}$。代码中的 `lora_A`、`lora_B` 与 PEFT 的目标模块配置对应 $A,B$；LoRA 减少可训练参数和优化器状态，不自动减少基座权重的推理显存。""",
    "50_model_evaluation.ipynb": r"""评测指标是对明确样本分布和测量协议的估计，不是模型的绝对属性。以准确率和成对胜率为例：

$$
\widehat{\mathrm{Acc}}=\frac{1}{N}\sum_{i=1}^{N}\mathbf 1(\hat y_i=y_i),\qquad
\widehat p_{\mathrm{win}}=\frac{W+0.5T}{N}
$$

其中，$N$ 是冻结评测集样本数，$W,T$ 分别为胜与平的数量。对于可独立近似的二项结果，正态近似标准误为 $\sqrt{\hat p(1-\hat p)/N}$；小样本、成对相关或分层数据应使用配对 Bootstrap 等方法。`my_classification_metrics` 对应确定性计数，`my_cluster_bootstrap_mean_ci` 对应按预先登记统计单位重采样的置信区间。逐例记录是统计单位，聚合表和置信区间是决策证据；不同任务、切片、Judge 或解码配置的分数不能直接压成无口径说明的总分。""",
    "60_inference_deployment.ipynb": r"""在线生成延迟由排队、Prefill、首 Token 返回和逐 Token Decode 共同构成。对输出 $N_{\mathrm{out}}$ 个 Token 的请求，可用以下关系建立容量基线：

$$
T_{\mathrm{e2e}}=T_{\mathrm{queue}}+T_{\mathrm{TTFT}}+(N_{\mathrm{out}}-1)T_{\mathrm{TPOT}},
\qquad \rho=\frac{\lambda}{c\mu}<1
$$

其中，$\lambda$ 是到达率，$\mu$ 是单 Worker 服务率，$c$ 是并行 Worker 数，$\rho$ 是利用率。`request_deadline`、Scheduler 队列和 Worker 指标分别承载这些变量。$\rho<1$ 只是稳态必要条件，不保证尾延迟达标；批处理、上下文长度、故障冗余和流量突发都必须进入容量压测。""",
    "70_model_safety.ipynb": r"""风险评估把发生可能性、影响和控制有效性变成可审计的相对排序，而不是宣称得到精确概率：

$$
R_{\mathrm{inherent}}=L\times I,\qquad
R_{\mathrm{residual}}=R_{\mathrm{inherent}}\left(1-E_{\mathrm{control}}\right)
$$

其中，$L$ 是发生可能性等级，$I$ 是影响等级，$E_{\mathrm{control}}\in[0,1]$ 是经过证据验证的控制有效性。代码中的风险登记表、控制测试和发布门禁分别对应输入、证据与决策。若等级来自序数尺度，乘积只适合排序和分层，不能解释为真实期望损失；高影响场景还需保留硬门禁、人工升级和残余风险接受责任。""",
    "90_llm_applications.ipynb": r"""RAG 的检索阶段目标是在有限证据预算内覆盖支持答案的文档，而不是仅最大化文本相似度。基础验收可写为：

$$
\operatorname{Recall@K}=\frac{|G_q\cap R_q^{(K)}|}{|G_q|},\qquad
\sum_{d\in R_q^{(K)}}\operatorname{tokens}(d)\le B_{\mathrm{ctx}}
$$

其中，$G_q$ 是问题 $q$ 的金标准证据集合，$R_q^{(K)}$ 是 Top-$K$ 检索结果，$B_{\mathrm{ctx}}$ 是为证据包分配的 Token 预算。`my_bm25_search` 产生候选，证据组装器实施预算约束，引用检查验证答案与证据的绑定关系。高 Recall@K 不等价于答案正确；生成器仍可能误读证据，缺少证据时还必须触发拒答。""",
    "91_prompt_reasoning.ipynb": r"""Self-Consistency 通过多次随机解码得到候选最终答案，并用多数票近似边缘化不同推理路径：

$$
\hat y=\arg\max_{a\in\mathcal A}\sum_{j=1}^{K}\mathbf 1\!\left(\operatorname{answer}(z_j)=a\right),
\qquad z_j\sim p_\theta(z\mid x;\tau)
$$

其中，$x$ 是提示，$z_j$ 是第 $j$ 条生成轨迹，$K$ 是采样次数，$\tau$ 是温度，$\mathcal A$ 是解析后的候选答案集合。`extract_final_answer` 对应答案解析，计数器对应投票聚合。增大 $K$ 会线性增加 Token 成本，且只有当轨迹具有一定独立性、解析稳定并且错误不高度相关时才可能改善结果。""",
    "A10_resource_planning.ipynb": r"""资源规划先把模型权重、运行时状态和峰值余量分开估算。推理显存下界可写为：

$$
M_{\mathrm{total}}\approx M_{\mathrm{weights}}+M_{\mathrm{KV}}+M_{\mathrm{activations}}+M_{\mathrm{runtime}}+M_{\mathrm{margin}},
\qquad M_{\mathrm{weights}}=P\frac{b_w}{8}
$$

其中，$P$ 是参数量，$b_w$ 是每个权重的存储位数，各 $M$ 的单位必须统一为 Byte 或 GiB。容量模型函数对应各项求和，实测峰值用于回填校准系数。公式是预算起点而非采购结论；量化元数据、临时 Workspace、碎片、并行复制和不同 Kernel 都会使实测值偏离理论下界。""",
    "A20_data_engineering.ipynb": r"""Packing 的目标是在不破坏样本原子边界和 Attention/Label 语义的前提下提高固定长度块的 Token 利用率：

$$
U_{\mathrm{pack}}=\frac{\sum_{i=1}^{N}L_i}{K\,L_{\mathrm{block}}},\qquad
K=\left\lceil\frac{\sum_i L_i+W}{L_{\mathrm{block}}}\right\rceil
$$

其中，$L_i$ 是第 $i$ 个样本的有效 Token 数，$L_{\mathrm{block}}$ 是块长，$K$ 是物化块数，$W$ 是分隔符及不可利用空位带来的额外 Token。`packer` 计算块布局，`attention_mask` 与 `labels` 保留边界语义，Shard Manifest 记录每片 Token 量。高利用率不等价于训练正确；跨样本可见性、EOS、Label Mask 和分布式 Shard 均衡必须分别验证。""",
    "A30_reasoning_model.ipynb": r"""推理模型工程把结果正确性、过程证据和计算预算分开建模。一个可审计的候选评分可写为：

$$
S(z)=w_oR_{\mathrm{outcome}}(z)+w_pR_{\mathrm{process}}(z)-\lambda C(z),
\qquad z^*=\arg\max_{z\in\mathcal Z_B}S(z)
$$

其中，$z$ 是候选轨迹，$R_{\mathrm{outcome}}$ 是结果验证分，$R_{\mathrm{process}}$ 是步骤验证分，$C(z)$ 是 Token、时间或调用成本，$\mathcal Z_B$ 是预算 $B$ 内的候选集合。Verifier、Parser 和预算控制器分别对应这些数学对象。权重只定义当前决策策略，不能把不可比的评分伪装成统一真值；原始推理轨迹也不应直接作为用户解释或审计日志。""",
    "A40_training_optimization.ipynb": r"""分布式训练必须先固定全局有效 Token 口径。若每卡 Micro-batch 为 $B_\mu$、序列有效 Token 均值为 $\bar L_{\mathrm{valid}}$、数据并行度为 $DP$、梯度累积步数为 $G$，则：

$$
T_{\mathrm{global}}=B_\mu\,\bar L_{\mathrm{valid}}\,DP\,G
$$

混合并行还要求被切分维度能够合法分片。以 Attention 为例，查询头数通常满足：

$$
N_q\bmod TP=0,\qquad N_q^{(\mathrm{rank})}=\frac{N_q}{TP}
$$

其中，$TP$ 是张量并行度。标准 MHA 中 $N_q=N_{kv}$；GQA 的 KV 头是否还需满足 $N_{kv}\bmod TP=0$，取决于 Runtime 是切分还是复制 KV 头。`DistributedSampler`、梯度累积器和并行配置分别对应 $DP,G,TP$；保持样本 Batch 不变但改变有效 Token 数，仍会改变优化语义。""",
    "A50_inference_optimization.ipynb": r"""KV Cache 复用历史 Token 的键和值，避免在每个 Decode 步骤重复投影，但历史 Cache 仍需被读取。忽略对齐和分页元数据时，其显存近似为：

$$
M_{\mathrm{KV}}\approx 2B L N_{\mathrm{layers}}N_{kv}d_h\frac{b}{8}
$$

其中，$B$ 是并发序列数，$L$ 是已缓存长度，$N_{kv}$ 是 KV 头数，$d_h$ 是每头维度，$b$ 是元素位数，系数 $2$ 表示 K 与 V。张量并行通常要求 $N_q\bmod TP=0$；若 KV 头按 Rank 切分，还要求 $N_{kv}\bmod TP=0$。支持 KV 头复制的 GQA/MQA Runtime 可放宽后一约束，但会改变显存和通信成本。`past_key_values`、Paged KV 分配器与服务指标分别对应数学状态、生产存储和实测校准。""",
    "A60_model_compression.ipynb": r"""压缩是在明确误差预算下减少参数、位宽或计算。截断 SVD 给出固定秩下的最优 Frobenius 范数近似：

$$
W=U\Sigma V^\top,\qquad W_r=U_{:,1:r}\Sigma_{1:r,1:r}V_{:,1:r}^\top,
\qquad \|W-W_r\|_F^2=\sum_{i>r}\sigma_i^2
$$

其中，$W\in\mathbb{R}^{m\times n}$，$r\le\min(m,n)$，$\sigma_i$ 是奇异值。量化则用比例尺 $s$ 和整数范围近似权重：$q=\operatorname{clip}(\operatorname{round}(W/s),q_{\min},q_{\max})$，$\hat W=sq$。代码中的 SVD、量化器和生产 Kernel 分别对应数学近似、制品编码与实际加速；矩阵误差更小不保证端到端质量更高，必须回到任务评测和硬件基准。""",
    "E10_open_model.ipynb": r"""Mixture-of-Experts（MoE）路由器为每个 Token 选择得分最高的 $k$ 个专家，并对其输出加权：

$$
p(e\mid x)=\operatorname{softmax}(W_rx),\qquad
\mathcal T_k(x)=\operatorname{TopK}_e\,p(e\mid x),\qquad
y=\sum_{e\in\mathcal T_k(x)}\tilde p_eE_e(x)
$$

其中，$x\in\mathbb{R}^{D}$ 是 Token 隐状态，$W_r\in\mathbb{R}^{E\times D}$ 是路由权重，$E$ 是专家数，$\tilde p_e$ 是 Top-$k$ 内重新归一化的权重。`my_topk_router` 对应路由选择，模型 `config.json` 记录专家数量与激活数量，生产 Expert Parallel Runtime 负责跨设备派发。该公式只说明通用稀疏路由语义，不能据此推断某个模型家族的实际路由损失、共享专家或通信实现。""",
    "E20_multimodal_llm.ipynb": r"""感知型视觉语言模型先把图像切成视觉 Token，再通过 Projector 对齐到语言模型隐藏维度并与文本 Token 拼接：

$$
N_v=\frac{H}{P_h}\frac{W}{P_w},\qquad
Z_v=f_{\mathrm{proj}}\!\left(f_{\mathrm{vision}}(I)\right)\in\mathbb{R}^{B\times N_v\times D_{\mathrm{llm}}}
$$

其中，$I\in\mathbb{R}^{B\times C\times H\times W}$，Patch 大小为 $P_h\times P_w$，$N_v$ 是未压缩视觉 Token 数。拼接后的序列长度为 $L=N_v+L_t+L_{\mathrm{special}}$；Label Mask 通常只让回答文本参与损失。`vision_encoder`、`projector/resampler`、`input_ids/inputs_embeds` 分别对应视觉编码、维度/长度对齐与语言模型输入。分辨率提高会以面积速度增加 Token，不等价于信息同比增加。""",
    "E30_nlp_bert.ipynb": r"""BERT 使用双向 Attention 建模上下文，并只在被选中的 Mask 位置计算 MLM 损失：

$$
H^{(0)}=E_{\mathrm{token}}+E_{\mathrm{position}}+E_{\mathrm{segment}},\qquad
\mathcal L_{\mathrm{MLM}}=-\frac{1}{|\mathcal M|}\sum_{t\in\mathcal M}\log p_\theta(x_t\mid x_{\setminus\mathcal M})
$$

其中，$H^{(0)}\in\mathbb{R}^{B\times L\times D}$，$\mathcal M$ 是参与预测的位置集合，$x_{\setminus\mathcal M}$ 表示经过 Mask 处理的上下文。`BertEmbeddings` 对应三类 Embedding 求和，`labels == -100` 对应不参与 MLM 损失的位置。双向可见性适合编码任务，但不能直接作为严格自回归生成的因果分解。""",
    "E40_cv_vit.ipynb": r"""ViT 把二维图像变为一维 Patch Token 序列，每个 Patch 展平后线性投影到模型隐藏维度：

$$
N=\frac{H}{P_h}\frac{W}{P_w},\qquad
X_{\mathrm{patch}}\in\mathbb{R}^{B\times N\times(CP_hP_w)},\qquad
Z=X_{\mathrm{patch}}W_E+b_E\in\mathbb{R}^{B\times N\times D}
$$

其中，$B,C,H,W$ 分别是批量、通道、高和宽，$P_h,P_w$ 是 Patch 尺寸，$D$ 是隐藏维度。加入 `[CLS]` 后序列长度为 $N+1$。`my_patchify` 对应重排，`nn.Conv2d(kernel_size=stride=P)` 同时实现切分与投影。公式假设图像尺寸可被 Patch 尺寸整除；生产预处理若采用裁剪、填充或位置编码插值，必须记录不同输入分辨率的语义变化。""",
    "E50_cv_diffusion.ipynb": r"""前向扩散用随时间增加的高斯噪声把数据逐步变为近似标准正态分布，并训练网络预测噪声或等价参数化：

$$
q(x_t\mid x_0)=\mathcal N\!\left(\sqrt{\bar\alpha_t}x_0,(1-\bar\alpha_t)I\right),\qquad
x_t=\sqrt{\bar\alpha_t}x_0+\sqrt{1-\bar\alpha_t}\,\epsilon
$$

$$
\mathcal L_{\epsilon}=\mathbb E_{x_0,t,\epsilon}\left[\|\epsilon-\epsilon_\theta(x_t,t,c)\|_2^2\right]
$$

其中，$x_0$ 是干净样本，$t$ 是时间步，$\bar\alpha_t$ 是累计信号保留率，$\epsilon\sim\mathcal N(0,I)$，$c$ 是可选条件。`my_add_noise`、噪声预测器与 Diffusers Scheduler 分别对应采样公式、学习目标和生产步进协议。不同 Scheduler 或 $v$-prediction 会改变训练/采样参数化，不能只替换函数名。""",
}


def section_number(notebook: nbformat.NotebookNode) -> str:
    """返回当前第 2 章下一个可用的小节编号。"""
    numbers: list[int] = []
    for cell in notebook.cells:
        if cell.cell_type != "markdown":
            continue
        if MARKER in cell.source:
            continue
        for match in re.finditer(r"^### 2\.(\d+)．", cell.source, re.MULTILINE):
            numbers.append(int(match.group(1)))
    return f"2.{max(numbers, default=0) + 1}"


def make_source(number: str, body: str) -> str:
    return (
        f"{MARKER}\n"
        f"### {number}．核心机制的语言与数学表达\n\n"
        f"{body.strip()}\n\n"
        "以上数学表示用于明确变量、形状与约束；实际结论仍需由本章的数值、形状、梯度、性能或失败案例证据验证。"
    )


def update_notebook(path: Path, body: str) -> str:
    notebook = nbformat.read(path, as_version=4)
    marked = [index for index, cell in enumerate(notebook.cells) if MARKER in cell.get("source", "")]
    source = make_source(section_number(notebook), body)

    if marked:
        first = marked[0]
        notebook.cells[first].source = source
        for index in reversed(marked[1:]):
            del notebook.cells[index]
        action = "updated"
    else:
        insert_at = next(
            (
                index
                for index, cell in enumerate(notebook.cells)
                if cell.cell_type == "markdown"
                and re.search(r"^## 3．", cell.source, re.MULTILINE)
            ),
            None,
        )
        if insert_at is None:
            raise ValueError(f"{path.name}: 未找到第 3 章插入点")
        notebook.cells.insert(insert_at, nbformat.v4.new_markdown_cell(source))
        action = "inserted"

    nbformat.validate(notebook)
    nbformat.write(notebook, path)
    return action


def main() -> None:
    actual = {path.name for path in ROOT.glob("*.ipynb")}
    expected = set(CONTENT)
    missing = actual - expected
    stale = expected - actual
    if missing or stale:
        raise SystemExit(f"Notebook 清单不一致: missing_content={sorted(missing)}, missing_files={sorted(stale)}")

    results = {name: update_notebook(ROOT / name, body) for name, body in sorted(CONTENT.items())}
    print(f"THEORY_MATH_CONTRACT notebooks={len(results)} inserted={sum(v == 'inserted' for v in results.values())} updated={sum(v == 'updated' for v in results.values())}")


if __name__ == "__main__":
    main()
