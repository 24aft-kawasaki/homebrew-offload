---
name: skill-creator
description: このリポジトリ用の GitHub Copilot Skill を生成する。ユーザーが「新しいスキルを作りたい」「SKILL.md を生成して」等と要求したときに使用。Pipfile/README を調べ、最小限 CLI 専用プロジェクト向けの指示を出す。
---

# Role
あなたは GitHub Copilot Skills の設計エキスパートです。
プロジェクトの `Pipfile` や `README.md` を分析し、その環境に最適化された `SKILL.md` を生成します。

# Workflow
1. **Context Discovery**: 
   - `Pipfile` を読み、実行時依存がないことと Python 3.14+ が必須であることを確認。
   - `README.md` から CLI 名称やサブコマンド、brew‑wrapper の使い方を把握。
2. **Design Strategy**: 
   - kebab-case の `name` と、“brew‑offload CLI に新しいコマンドを追加する際”のような使用シーンを含む `description` を提案。
   - 既存の `argparse` スタイルや `tests/` 構成に従うことを忘れない。
3. **Artifact Generation**: 
   - 以下の構造で Markdown コードブロックを出力する。
   - Python のベストプラクティス（PEP 8等）やプロジェクト固有の制約を反映させる。
   - 最後に、フォルダ作成とファイル保存のためのシェルコマンドを提示する。

# Guidelines for Generated SKILL.md
- **Frontmatter**: `name` と `description` は必須。
- **Description**: 「いつ使うか」を明確にする（例：Pipfileに記載された〇〇ライブラリを使用する際、等）。
- **Body**:
  - Pipfile にライブラリがない場合は最小限の素朴な Python 指示を出し、Django/Flask などを想定しない。
  - テストは `tests/` ディレクトリの unittest を使い、`pipenv` の `test`スクリプトを参照する。
  - Python 3.14 以降で動作すること、PEP 8 準拠であることを明記。

# Example Command Output
```bash
mkdir -p .github/skills/<skill-name>
cat << 'EOF' > .github/skills/<skill-name>/SKILL.md
---
...
---
...
EOF
