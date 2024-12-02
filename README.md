# Novel-Split 使用说明

## 功能简介

`Novel-Split` 是一款智能小说章节拆分工具，可以将整篇小说按照章节结构拆分为独立部分。适用于需要整理小说内容或进行内容管理的用户。

---

## 功能特点

- **智能章节识别**：基于关键字、章节格式和NLP Rewards自动拆分小说。
- **高效处理**：快速将小说拆分成清晰的章节结构。
- **可定制分章规则**：支持用户自定义章节标题识别规则（如“第xx章”“Chapter xx”等）。
- **输出格式灵活**：分章后的内容可导出为索引昵称保存或章节昵称保存。

---

## 安装方法

### 1. 克隆项目

```bash
git clone https://github.com/Anning01/novel-split.git
cd novel-split
pip install -r requirements.txt
```

## 使用步骤

### 1. 运行程序

```bash
python main.py --input <输入文件路径> --output <输出文件夹路径>
python nlp.py --input <输入文件路径> --output <输出文件夹路径>
```

### 2. 参数说明

- `--input`：输入文件路径，例如 `novel.txt`。
- `--output`：输入文件路径，例如 `output/`。

### 3. 示例

```bash
python main.py --input novel.txt --output chapters/
python nlp.py --input novel.txt --output chapters/
```

## 输出结果

### 1. 按章节分文件 (nlp.py)

```bash
chapters/
├── 1第一章：xxx.txt
├── 2第二章：xxx.txt
├── ...
```


### 2. 索引拆分（main.py 重复章节索引会合并）
```bash
chapters/
├── 1.txt
├── 2.txt
├── ...
```

## 注意事项
1. 确保输入文件为纯文本或支持的格式（如 .txt）。
2. 推荐使用nlp，更加准确
3. 生成的目录在temp下
4. 如果有一些章节遗漏，可以考虑修改final_score分数相似度 默认0.7


## 贡献代码
欢迎提交 Issue 或 Pull Request 来改进项目。请访问 GitHub 项目地址。

## 感谢开源
本项目基于以下开源项目进行开发：
- [nltk](https://github.com/nltk/nltk)
- [TXT-Automatic-Chaptering](https://github.com/elysia-best/TXT-Automatic-Chaptering)


