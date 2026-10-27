# 金属材料期刊导航

一个面向金属材料、高熵合金和结构材料研究的期刊投稿要求查询与对比网页。

首版收录 17 本常投期刊，按照便于选刊的导航梯队组织：

- 正刊：Nature、Science
- 大子刊：Nature Materials、Nature Communications、Science Advances
- 小子刊：Communications Materials
- 材料综合旗舰刊：Advanced Materials、Materials Today、PNAS
- 金属材料核心刊：Acta Materialia、Scripta Materialia、MSEA、JMST、JAC、Materials & Design、Intermetallics、Corrosion Science

> “投稿梯队”只是本站的检索导航，不是官方排名，也不等同于影响因子、中科院分区或录用难度。

## 功能

- 中英文关键词检索期刊名、缩写、研究方向和定位
- 按投稿梯队、出版社、研究方向和 OA 模式组合筛选
- 在“深度投稿工作台”先查看默认稿件类型、证据范围、核验日期和官方来源
- 用“投稿硬参数速查”直接查摘要字数、正文骨架、图表数量、分图大小写、图注和参考文献格式
- 每项同时标出“官方规则”“本站建议”和证据等级，并可点击回到对应官方原文
- 按期刊查看可直接照着组织正文的“推荐排稿骨架”，而不是使用通用示意图
- 按题目、摘要、关键词、引言、方法、结果、讨论、结论、图表、参考文献和声明逐项查看格式要求
- 查看初投稿文件、图片分辨率、图注、表格、补充信息和数据/代码声明等技术规格
- 直接打开官方作者指南、Word/LaTeX 模板、官方写作示例或已发表论文实例
- 每本期刊精选 3 篇金属材料/高熵合金相关论文，并说明推荐理由和应重点观察的写作部分
- 在官方要求之后查看本站整理的选刊契合点、风险和投稿前检查清单
- 选择 2–4 本期刊并排比较
- 每本期刊提供官网、官方作者指南、核验日期和核验状态
- 将不确定项解释为“按文章类型变化”“官网未给统一值”或“以投稿系统为准”，并写明原因
- 记录超过 180 天未核验时，在期刊卡片和对比表中显示过期提示

## 在线使用

部署完成后访问：<https://materials-journal-guide.streamlit.app/>

## 本地运行

需要 Python 3.11 或更高版本。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

浏览器打开终端显示的本地地址，通常是 `http://localhost:8501`。

## 测试

```powershell
python -m pip install -e ".[test]"
python -m pytest -v
```

测试覆盖：

- YAML 必填字段、重复记录、HTTPS 来源和核验日期
- 首批 17 本期刊的完整性和稳定排序
- 中英文搜索、组合筛选、对比数量上限和未知 ID
- Streamlit 启动、核心控件和两刊对比
- 17 本期刊的官方格式覆盖、逐项来源、证据范围和资源链接
- Nature、Nature Materials、Advanced Materials 的关键字数、结构和图表限制
- Nature、Nature Communications、Nature Materials、Communications Materials、Advanced Materials 与 PNAS 的分图和参考文献格式
- 六项硬参数字段完整性、具体建议、HTTPS 官方来源和禁止模糊占位语
- 本刊专属、出版社通用和官网未公开稳定值三类证据边界

## 数据结构

正式数据源是 [`data/journals.yaml`](data/journals.yaml)。每条记录包含：

- `id`、`name`、`abbreviation`、`publisher`
- `tier`、`tier_order`、`topics`、`scope`
- `article_types`、`initial_submission`
- `abstract_limit`、`word_limit`
- `graphical_abstract`、`highlights`
- `references`、`figures`、`data_policy`
- `oa_model`、`peer_review`、`special_notes`
- `homepage_url`、`guide_url`、`source_urls`
- `verified_on`、`verification_status`

官方格式数据位于 [`data/journal_official_requirements.yaml`](data/journal_official_requirements.yaml)。每本期刊都包含默认稿件类型、证据范围、核验日期、逐章节格式、文件与技术规格、官方来源以及模板/实例资源。加载器要求全部条目使用 HTTPS 官方来源，并拒绝缺失期刊、空白来源、未知证据类型和旧占位语。

投稿硬参数位于 [`data/journal_format_specs.yaml`](data/journal_format_specs.yaml)。17 本期刊分别维护摘要、正文骨架、图表数量、分图标注、图注、参考文献六项速查，以及至少五步的推荐排稿骨架。每项必须同时包含官方规则、本站建议、证据等级和 HTTPS 来源；官网没有固定上限时必须明确写出，并给出带数字的本站排稿建议，不能用“以官网为准”等空话代替。

精选论文位于 [`data/journal_examples.yaml`](data/journal_examples.yaml)。每本期刊固定 3 篇真实论文，每篇记录题名、年份、文章类型、主题、DOI/出版社链接、推荐理由和观察重点。加载器会拒绝缺刊、数量不是 3、重复链接、无效年份和非 HTTPS 来源。论文实例只用于观察真实呈现，不是期刊模板或编辑部推荐。

证据范围分为：

- `期刊专属`：本刊官网明确给出的要求，例如 Nature 的 75 字符题目、200 词概要段和图注限制。
- `出版社通用`：出版社统一写作或技术规范，例如 Elsevier 的章节结构、图片分辨率和表格规则；页面不会把它冒充为某一本期刊的专属数字。
- `官网未公开稳定值`：官方入口存在，但当前页面没有可稳定读取、可泛化到全部原创研究稿件的固定数值；页面保留问题和官方入口，不用二手数字补空。

写作策略数据位于 [`data/journal_guidance.yaml`](data/journal_guidance.yaml)：共享画像提供文章结构和自查清单，17 本期刊分别提供编辑切入点、适合信号和风险信号。该文件属于本站建议，并在页面中降为次级信息，不是出版社规则。

修改后必须执行 `python -m pytest -v`。不允许删除核验日期或用第三方博客替代官方来源。

## 证据边界

- 硬性投稿要求只来自期刊官网或出版社作者指南。
- 默认整理原创研究论文；Review、Perspective、Letter 等可能有独立要求。
- 首版不固定展示易变化的影响因子、分区、APC 和非官方审稿时长。
- 官网未明确、页面受地区限制或要求随文章类型变化时，网页显示“官网未公开稳定值”及官方入口，不用二手信息补空。
- “本站写作建议”与“官方要求”使用不同标签和数据文件；官方要求始终排在本站建议之前。
- 硬性数字、官方排版惯例、官网未设固定上限和本站建议分别标注；建议数字不会冒充期刊限制。
- “官方模板”“官方示例”和“已发表论文实例”分别标注；实例只用于观察真实呈现，不会被描述成强制模板。
- `verified_on` 距当前日期超过 180 天时，网页会提示重新核验。
- 网页用于准备投稿清单，不能替代作者在正式提交当天阅读官方指南。

## 更新期刊信息

请阅读 [`CONTRIBUTING.md`](CONTRIBUTING.md)。建议每 3–6 个月巡检一次，并在出版社更新作者指南后优先复核。

## Streamlit Community Cloud 部署

1. 将仓库推送到 GitHub。
2. 在 Streamlit Community Cloud 新建应用。
3. Repository 选择本仓库，Branch 选择 `main`。
4. Main file path 填写 `app.py`。
5. 部署后检查首页、筛选器、投稿硬参数速查、推荐排稿骨架、官方要求总览、逐节格式、技术规格、资源链接和对比表。

该项目不需要 API Key 或其他 Secrets。
