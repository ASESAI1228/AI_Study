#!/bin/bash

# Topic navigation HTML to insert
TOPIC_NAV='<!-- Topic-based navigation -->
<div class="blog-topics">
    <h3>トピック別ブログ記事</h3>
    <p>他のトピックの記事も読む：</p>
    <ul>
        <li><a href="index.html#ai-basics">AI基礎</a></li>
        <li><a href="index.html#machine-learning">機械学習</a></li>
        <li><a href="index.html#llm">大規模言語モデル</a></li>
        <li><a href="index.html#prompt-engineering">プロンプトエンジニアリング</a></li>
        <li><a href="index.html#ai-services">AIサービス</a></li>
        <li><a href="index.html#legal-ai-cases">法務AI活用事例</a></li>
        <li><a href="index.html#ai-ethics">AI倫理と法的課題</a></li>
    </ul>
</div>

<!-- Previous/Next navigation -->'

# Process all HTML files except index.html
for file in $(find . -name "*.html" ! -name "index.html"); do
  # Check if file already has the topic navigation
  if ! grep -q "blog-topics" "$file"; then
    # Replace the blog-navigation div with our new navigation
    sed -i "s|<div class=\"blog-navigation\">|$TOPIC_NAV\n<div class=\"blog-navigation\">|g" "$file"
    echo "Updated $file"
  else
    echo "Skipping $file (already has topic navigation)"
  fi
done
