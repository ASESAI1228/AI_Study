#!/bin/bash

# Process all HTML files except index.html
for file in $(find . -name "*.html" ! -name "index.html" ! -name "topic_nav_template.html"); do
  # Check if file already has the topic navigation
  if ! grep -q "blog-topics" "$file"; then
    # Create a backup of the original file
    cp "$file" "${file}.bak"
    
    # Manually insert the navigation template before the footer
    sed -i '/<footer>/i <!-- Topic-based navigation -->\n<div class="blog-topics">\n    <h3>トピック別ブログ記事</h3>\n    <p>他のトピックの記事も読む：</p>\n    <ul>\n        <li><a href="index.html#ai-basics">AI基礎</a></li>\n        <li><a href="index.html#machine-learning">機械学習</a></li>\n        <li><a href="index.html#llm">大規模言語モデル</a></li>\n        <li><a href="index.html#prompt-engineering">プロンプトエンジニアリング</a></li>\n        <li><a href="index.html#ai-services">AIサービス</a></li>\n        <li><a href="index.html#legal-ai-cases">法務AI活用事例</a></li>\n        <li><a href="index.html#ai-ethics">AI倫理と法的課題</a></li>\n    </ul>\n</div>\n\n<!-- Previous/Next navigation -->\n' "$file"
    
    # Check if the file was modified successfully
    if [ $? -ne 0 ]; then
      echo "Error: Failed to update $file. Restoring from backup."
      mv "${file}.bak" "$file"
    else
      echo "Updated $file"
      rm "${file}.bak"
    fi
  else
    echo "Skipping $file (already has topic navigation)"
  fi
done
