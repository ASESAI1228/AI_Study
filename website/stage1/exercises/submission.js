/**
 * 課題提出フォームの処理を行うJavaScript
 */
document.addEventListener('DOMContentLoaded', function() {
    const exerciseSubmissionForm = document.getElementById('exerciseSubmissionForm');
    const saveProgressButton = document.getElementById('saveProgress');
    
    if (exerciseSubmissionForm) {
        // 文字数カウンター機能の追加
        setupCharacterCounters();
        
        // フォームの送信処理
        exerciseSubmissionForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // バリデーション
            if (!validateForm()) {
                showMessage('必須項目をすべて入力してください。文字数制限も確認してください。', 'error');
                return;
            }
            
            // フォームデータの収集
            const formData = collectFormData();
            
            try {
                // Supabaseが初期化されているか確認
                if (!supabaseClient) {
                    throw new Error('データベース接続が初期化されていません。');
                }
                
                // ユーザーIDの取得（実際の実装ではログイン機能と連携）
                const { data: { user } } = await supabaseClient.auth.getUser();
                if (!user) {
                    throw new Error('ユーザー情報が取得できません。');
                }
                
                // データの保存
                const result = await saveSubmission(formData, user.id, true);
                
                if (result.error) {
                    throw new Error(result.error.message);
                }
                
                showMessage('課題が正常に提出されました。', 'success');
            } catch (error) {
                console.error('提出エラー:', error);
                showMessage(`提出中にエラーが発生しました: ${error.message}`, 'error');
            }
        });
        
        // 途中経過保存処理
        if (saveProgressButton) {
            saveProgressButton.addEventListener('click', async function() {
                // フォームデータの収集（バリデーションなし）
                const formData = collectFormData(false);
                
                try {
                    // Supabaseが初期化されているか確認
                    if (!supabaseClient) {
                        throw new Error('データベース接続が初期化されていません。');
                    }
                    
                    // ユーザーIDの取得
                    const { data: { user } } = await supabaseClient.auth.getUser();
                    if (!user) {
                        throw new Error('ユーザー情報が取得できません。');
                    }
                    
                    // データの保存（下書きとして）
                    const result = await saveSubmission(formData, user.id, false);
                    
                    if (result.error) {
                        throw new Error(result.error.message);
                    }
                    
                    showMessage('途中経過が保存されました。', 'success');
                } catch (error) {
                    console.error('保存エラー:', error);
                    showMessage(`保存中にエラーが発生しました: ${error.message}`, 'error');
                }
            });
        }
        
        // 保存済みデータの読み込み
        loadSavedData();
    }
    
    // 文字数カウンター機能のセットアップ
    function setupCharacterCounters() {
        const textareas = document.querySelectorAll('textarea[data-min-chars], textarea[data-max-chars]');
        
        textareas.forEach(textarea => {
            // カウンター要素の作成
            const counterDiv = document.createElement('div');
            counterDiv.className = 'character-counter';
            textarea.after(counterDiv);
            
            // 入力イベントでカウンターを更新
            textarea.addEventListener('input', function() {
                updateCharacterCount(textarea, counterDiv);
            });
            
            // 初期カウント表示
            updateCharacterCount(textarea, counterDiv);
        });
    }
    
    // 文字数カウンターの更新
    function updateCharacterCount(textarea, counterElement) {
        const currentLength = textarea.value.length;
        const minChars = parseInt(textarea.dataset.minChars) || 0;
        const maxChars = parseInt(textarea.dataset.maxChars) || Infinity;
        
        // カウンターテキストの設定
        counterElement.textContent = `${currentLength} 文字`;
        
        // 文字数に応じたスタイル変更
        if (maxChars < Infinity) {
            counterElement.textContent += ` / ${maxChars} 文字`;
        }
        
        // 文字数制限のスタイル
        if (currentLength < minChars) {
            counterElement.className = 'character-counter warning';
            textarea.classList.add('error');
        } else if (maxChars < Infinity && currentLength > maxChars) {
            counterElement.className = 'character-counter error';
            textarea.classList.add('error');
        } else {
            counterElement.className = 'character-counter';
            textarea.classList.remove('error');
        }
    }
    
    // フォームバリデーション
    function validateForm() {
        let isValid = true;
        const requiredFields = exerciseSubmissionForm.querySelectorAll('[required]');
        
        // 必須フィールドのチェック
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('error');
                
                // エラーメッセージの表示
                const errorMessage = field.nextElementSibling;
                if (errorMessage && errorMessage.classList.contains('error-message')) {
                    errorMessage.style.display = 'block';
                }
            } else {
                field.classList.remove('error');
                
                // エラーメッセージの非表示
                const errorMessage = field.nextElementSibling;
                if (errorMessage && errorMessage.classList.contains('error-message')) {
                    errorMessage.style.display = 'none';
                }
            }
        });
        
        // 文字数制限のチェック
        const textareas = exerciseSubmissionForm.querySelectorAll('textarea[data-min-chars], textarea[data-max-chars]');
        textareas.forEach(textarea => {
            const currentLength = textarea.value.length;
            const minChars = parseInt(textarea.dataset.minChars) || 0;
            const maxChars = parseInt(textarea.dataset.maxChars) || Infinity;
            
            if (currentLength < minChars || (maxChars < Infinity && currentLength > maxChars)) {
                isValid = false;
                textarea.classList.add('error');
            }
        });
        
        return isValid;
    }
    
    // フォームデータの収集
    function collectFormData(validate = true) {
        const formData = {
            exercise_id: exerciseSubmissionForm.dataset.exerciseId,
            answers: {},
            submitted: validate, // 提出済みかどうか
            submitted_at: new Date().toISOString()
        };
        
        // テキストエリアの値を収集
        const textareas = exerciseSubmissionForm.querySelectorAll('textarea[data-question-id]');
        textareas.forEach(textarea => {
            const questionId = textarea.dataset.questionId;
            formData.answers[questionId] = textarea.value.trim();
        });
        
        return formData;
    }
    
    // Supabaseにデータを保存
    async function saveSubmission(formData, userId, isSubmitted) {
        return supabaseClient.from('exercise_submissions')
            .insert({
                user_id: userId,
                exercise_id: formData.exercise_id,
                answers: formData.answers,
                is_submitted: isSubmitted,
                submitted_at: formData.submitted_at
            })
            .then(response => {
                return response;
            });
    }
    
    // 保存済みデータの読み込み
    async function loadSavedData() {
        try {
            // Supabaseが初期化されているか確認
            if (!supabaseClient) {
                console.warn('データベース接続が初期化されていません。保存データを読み込めません。');
                return;
            }
            
            // ユーザーIDの取得
            try {
                const { data: { user } } = await supabaseClient.auth.getUser();
                if (!user) {
                    console.warn('ユーザー情報が取得できません。保存データを読み込めません。');
                    return;
                }
            } catch (error) {
                console.warn('ユーザー情報が取得できません。保存データを読み込めません。', error);
                return;
            }
            
            const exerciseId = exerciseSubmissionForm.dataset.exerciseId;
            
            // 最新の保存データを取得
            const result = await supabaseClient.from('exercise_submissions')
                .select('*')
                .eq('user_id', user.id)
                .eq('exercise_id', exerciseId)
                .then(response => {
                    return response;
                });
            
            if (result.error) {
                throw new Error(result.error.message);
            }
            
            // データが存在する場合、フォームに入力
            if (result.data && result.data.length > 0) {
                // 最新のデータを使用
                const latestSubmission = result.data.sort((a, b) => 
                    new Date(b.submitted_at) - new Date(a.submitted_at)
                )[0];
                
                // フォームに値を設定
                const answers = latestSubmission.answers;
                for (const questionId in answers) {
                    const textarea = exerciseSubmissionForm.querySelector(`textarea[data-question-id="${questionId}"]`);
                    if (textarea) {
                        textarea.value = answers[questionId];
                        
                        // 文字数カウンターの更新
                        const counterDiv = textarea.nextElementSibling;
                        if (counterDiv && counterDiv.classList.contains('character-counter')) {
                            updateCharacterCount(textarea, counterDiv);
                        }
                    }
                }
                
                // 提出済みの場合はメッセージを表示
                if (latestSubmission.is_submitted) {
                    showMessage('この課題は既に提出されています。再提出も可能です。', 'info');
                } else {
                    showMessage('保存された途中経過を読み込みました。', 'info');
                }
            }
        } catch (error) {
            console.error('データ読み込みエラー:', error);
        }
    }
    
    // メッセージ表示
    function showMessage(message, type) {
        // 既存のメッセージを削除
        const existingStatus = document.querySelector('.submission-status');
        if (existingStatus) {
            existingStatus.remove();
        }
        
        // 新しいメッセージ要素を作成
        const statusElement = document.createElement('div');
        statusElement.className = `submission-status submission-${type}`;
        statusElement.textContent = message;
        statusElement.style.display = 'block';
        
        // フォームの後に挿入
        exerciseSubmissionForm.after(statusElement);
        
        // 一定時間後に消える（エラーメッセージ以外）
        if (type !== 'error') {
            setTimeout(() => {
                statusElement.style.opacity = '0';
                statusElement.style.transition = 'opacity 0.5s';
                setTimeout(() => statusElement.remove(), 500);
            }, 5000);
        }
    }
});
