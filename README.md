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
- 查看初投格式、文章类型、篇幅、图文摘要、图片、参考文献和数据政策
- 在“深度投稿工作台”查看每本期刊的编辑切入点、适合信号和常见风险
- 用文章结构地图和原创 SVG 主图蓝图搭建金属材料论文叙事
- 用可勾选清单检查证据链、图件、统计、数据声明和投稿文件
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
- 17 本期刊的写作画像覆盖、结构/图稿蓝图和证据状态解释

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

写作策略数据位于 [`data/journal_guidance.yaml`](data/journal_guidance.yaml)：共享画像提供文章结构、主图叙事和清单，17 本期刊分别提供编辑切入点、适合信号和风险信号。该文件属于本站建议，不是出版社规则。

修改后必须执行 `python -m pytest -v`。不允许删除核验日期或用第三方博客替代官方来源。

## 证据边界

- 硬性投稿要求只来自期刊官网或出版社作者指南。
- 默认整理原创研究论文；Review、Perspective、Letter 等可能有独立要求。
- 首版不固定展示易变化的影响因子、分区、APC 和非官方审稿时长。
- 官网未明确、页面受地区限制或要求随文章类型变化时，网页显示具体证据状态和不确定原因，不用二手信息补空。
- “本站写作建议”与“官方要求”在页面上使用不同标签；主图蓝图为原创示意，不复制已发表论文图片，也不是期刊强制模板。
- `verified_on` 距当前日期超过 180 天时，网页会提示重新核验。
- 网页用于准备投稿清单，不能替代作者在正式提交当天阅读官方指南。

## 更新期刊信息

请阅读 [`CONTRIBUTING.md`](CONTRIBUTING.md)。建议每 3–6 个月巡检一次，并在出版社更新作者指南后优先复核。

## Streamlit Community Cloud 部署

1. 将仓库推送到 GitHub。
2. 在 Streamlit Community Cloud 新建应用。
3. Repository 选择本仓库，Branch 选择 `main`。
4. Main file path 填写 `app.py`。
5. 部署后检查首页、筛选器、官方链接和对比表。

该项目不需要 API Key 或其他 Secrets。
