/**
 * サンプル文書タブ切り替え機能
 * @param {Event} event - クリックイベント
 * @param {string} tabName - 表示するタブのID
 */
function openSampleTab(event, tabName) {
    // すべてのタブコンテンツを非表示
    const tabContents = document.getElementsByClassName('sample-content');
    for (let i = 0; i < tabContents.length; i++) {
        tabContents[i].classList.remove('active');
    }

    // すべてのタブリンクから active クラスを削除
    const tabLinks = document.getElementsByClassName('tablink');
    for (let i = 0; i < tabLinks.length; i++) {
        tabLinks[i].classList.remove('active');
    }

    // クリックされたタブのコンテンツを表示
    document.getElementById(tabName).classList.add('active');
    
    // クリックされたタブリンクに active クラスを追加
    event.currentTarget.classList.add('active');
}

/**
 * サンプルテキストをクリップボードにコピー
 * @param {string} elementId - コピー対象のテキスト要素のID
 */
async function copySampleText(elementId) {
    const textElement = document.getElementById(elementId);
    if (!textElement) return;
    
    // ファイルパスをIDから特定
    let filePath = '';
    if (elementId === 'contract-content') {
        filePath = '../samples/contract-sample.txt';
    } else if (elementId === 'legal-question-content') {
        filePath = '../samples/legal-question-sample.txt';
    } else if (elementId === 'case-law-content') {
        filePath = '../samples/case-law-sample.txt';
    }
    
    try {
        // ファイルの完全なテキストを取得
        const response = await fetch(filePath);
        if (!response.ok) {
            throw new Error(`ファイルの取得に失敗しました: ${response.status}`);
        }
        
        const fullText = await response.text();
        
        // モダンなクリップボードAPIを使用
        if (navigator.clipboard) {
            await navigator.clipboard.writeText(fullText);
        } else {
            // フォールバック: 一時的な要素に全文を入れてコピー
            const tempElement = document.createElement('textarea');
            tempElement.value = fullText;
            document.body.appendChild(tempElement);
            tempElement.select();
            document.execCommand('copy');
            document.body.removeChild(tempElement);
        }
        
        // コピー成功メッセージを表示
        const copyButton = document.querySelector(`button[onclick="copySampleText('${elementId}')"]`);
        if (copyButton) {
            const originalText = copyButton.textContent;
            copyButton.textContent = '全文コピー完了！';
            
            // 2秒後に元のテキストに戻す
            setTimeout(() => {
                copyButton.textContent = originalText;
            }, 2000);
        }
    } catch (err) {
        console.error('コピーに失敗しました:', err);
        alert('コピーに失敗しました: ' + err.message);
    }
}

// モダンなクリップボードAPIを使用したコピー関数（フォールバック用）
function copyTextToClipboard(text) {
    if (!navigator.clipboard) {
        return false;
    }
    
    navigator.clipboard.writeText(text)
        .then(() => {
            console.log('テキストがクリップボードにコピーされました');
            return true;
        })
        .catch(err => {
            console.error('クリップボードへのコピーに失敗しました:', err);
            return false;
        });
}

// ページ読み込み時に初期タブを設定
document.addEventListener('DOMContentLoaded', function() {
    // サンプル文書タブの初期化
    const sampleTabs = document.querySelectorAll('.sample-documents-tabs .tablink');
    if (sampleTabs.length > 0) {
        // 最初のタブをアクティブに設定
        const firstTab = sampleTabs[0];
        const firstTabId = firstTab.textContent.includes('契約書') ? 'contract' : 
                          firstTab.textContent.includes('法的質問') ? 'legal-question' : 'case-law';
        
        // 対応するコンテンツを表示
        const tabContents = document.getElementsByClassName('sample-content');
        for (let i = 0; i < tabContents.length; i++) {
            tabContents[i].classList.remove('active');
        }
        
        if (document.getElementById(firstTabId)) {
            document.getElementById(firstTabId).classList.add('active');
        }
    }
});
