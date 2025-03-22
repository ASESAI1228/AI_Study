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
                
                // ユーザーIDの取得（匿名ユーザーIDを生成）
                let user;
                try {
                    // 匿名サインインが無効なため、ローカルストレージを使用して一貫したユーザーIDを提供
                    let userId = localStorage.getItem('anonymous_user_id');
                    if (!userId) {
                        // ランダムなユーザーIDを生成して保存
                        userId = 'anon_' + Math.random().toString(36).substring(2, 15) + 
                                Math.random().toString(36).substring(2, 15);
                        localStorage.setItem('anonymous_user_id', userId);
                    }
                    
                    console.log('Using local anonymous user ID:', userId);
                    
                    // 匿名ユーザーオブジェクトを作成
                    user = {
                        id: userId,
                        email: 'anonymous@example.com',
                        role: 'anonymous'
                    };
                } catch (error) {
                    console.error('User ID generation error:', error);
                    throw new Error('ユーザーIDの生成に失敗しました: ' + error.message);
                }
                
                // データの保存
                const result = await saveSubmission(formData, user.id, true);
                
                if (result.error) {
                    throw new Error(result.error.message);
                }
                
                // 採点プロセスを開始
                try {
                    // 採点進捗表示のための要素を作成
                    const gradingProgressElement = document.createElement('div');
                    gradingProgressElement.className = 'grading-progress';
                    gradingProgressElement.innerHTML = `
                        <div class="progress-bar" style="width: 0%"></div>
                        <div class="progress-status">採点を準備しています...</div>
                    `;
                    
                    // フォームの下に挿入
                    exerciseSubmissionForm.after(gradingProgressElement);
                    showMessage('課題が提出されました。AIによる採点を行っています...', 'info');
                    
                    // 進捗更新関数
                    const updateProgress = (percent, statusText) => {
                        const progressBar = gradingProgressElement.querySelector('.progress-bar');
                        const progressStatus = gradingProgressElement.querySelector('.progress-status');
                        
                        progressBar.style.width = `${percent}%`;
                        progressStatus.textContent = statusText;
                    };
                    
                    // OpenAIクライアントが初期化されているか確認
                    if (!openaiClient) {
                        throw new Error('AIグレーディングシステムの初期化に失敗しました。');
                    }
                    
                    // 採点を実行
                    const exerciseId = exerciseSubmissionForm.dataset.exerciseId;
                    const gradingResult = await openaiClient.createGradingAssessment(
                        exerciseId, 
                        formData.answers,
                        updateProgress
                    );
                    
                    // 採点結果表示
                    gradingProgressElement.remove();
                    displayGradingResults(gradingResult, exerciseId);
                    
                    // 採点結果をSupabaseに保存
                    try {
                        const { error: gradingError } = await supabaseClient.saveGradingResults({
                            submission_id: result.data.id,
                            grading_results: gradingResult
                        });
                        
                        if (gradingError) {
                            console.error('Failed to save grading results:', gradingError);
                            // Fallback to localStorage
                            localStorage.setItem(`grading_${result.data.id}`, JSON.stringify(gradingResult));
                        } else {
                            console.log('Grading results saved successfully');
                        }
                    } catch (gradingStoreError) {
                        console.error('Error saving grading results:', gradingStoreError);
                        // Fallback to localStorage
                        localStorage.setItem(`grading_${result.data.id}`, JSON.stringify(gradingResult));
                    }
                    
                } catch (gradingError) {
                    console.error('採点エラー:', gradingError);
                    showMessage(`採点中にエラーが発生しました: ${gradingError.message}`, 'error');
                    
                    if (result.source === 'localStorage') {
                        showMessage('課題は正常に提出されましたが、採点できませんでした（ローカルストレージに保存）。', 'success');
                    } else {
                        showMessage('課題は正常に提出されましたが、採点できませんでした。', 'success');
                    }
                }
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
                    
                    // ユーザーIDの取得（匿名ユーザーIDを生成）
                    let user;
                    try {
                        // 匿名サインインが無効なため、ローカルストレージを使用して一貫したユーザーIDを提供
                        let userId = localStorage.getItem('anonymous_user_id');
                        if (!userId) {
                            // ランダムなユーザーIDを生成して保存
                            userId = 'anon_' + Math.random().toString(36).substring(2, 15) + 
                                    Math.random().toString(36).substring(2, 15);
                            localStorage.setItem('anonymous_user_id', userId);
                        }
                        
                        console.log('Using local anonymous user ID:', userId);
                        
                        // 匿名ユーザーオブジェクトを作成
                        user = {
                            id: userId,
                            email: 'anonymous@example.com',
                            role: 'anonymous'
                        };
                    } catch (error) {
                        console.error('User ID generation error:', error);
                        throw new Error('ユーザーIDの生成に失敗しました: ' + error.message);
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
        
        // 文字数制限のチェック - 一時的に緩和
        const textareas = exerciseSubmissionForm.querySelectorAll('textarea[data-min-chars], textarea[data-max-chars]');
        textareas.forEach(textarea => {
            const currentLength = textarea.value.length;
            const minChars = parseInt(textarea.dataset.minChars) || 0;
            const maxChars = parseInt(textarea.dataset.maxChars) || Infinity;
            
            // 文字数制限を緩和（最低文字数を300に、最大文字数を制限なしに）
            const adjustedMinChars = Math.min(minChars, 300);
            
            if (currentLength < adjustedMinChars) {
                isValid = false;
                textarea.classList.add('error');
            } else {
                textarea.classList.remove('error');
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
    
    // Supabaseにデータを保存（ローカルストレージをフォールバックとして使用）
    async function saveSubmission(formData, userId, isSubmitted) {
        try {
            // まずSupabaseへの保存を試みる
            const submissionData = {
                exercise_type: formData.exercise_id,
                user_id: userId,
                submission_date: formData.submitted_at,
                content: {
                    answers: formData.answers,
                    is_submitted: isSubmitted
                }
            };
            
            const { data, error } = await supabaseClient.from('prompt_exercise_submissions')
                .insert(submissionData);
                
            if (error) {
                console.warn('Supabase submission error:', error);
                console.log('Falling back to localStorage for submission');
                
                // ローカルストレージにフォールバック
                const submission = {
                    user_id: userId,
                    exercise_id: formData.exercise_id,
                    answers: formData.answers,
                    is_submitted: isSubmitted,
                    submitted_at: formData.submitted_at
                };
                
                // 既存の提出を取得
                const savedSubmissions = JSON.parse(localStorage.getItem('exercise_submissions') || '[]');
                savedSubmissions.push(submission);
                localStorage.setItem('exercise_submissions', JSON.stringify(savedSubmissions));
                
                console.log('Saved submission to localStorage');
                return { data: submission, error: null, source: 'localStorage' };
            }
            
            return { data, error, source: 'supabase' };
        } catch (error) {
            console.error('Submission error:', error);
            
            // エラー発生時もローカルストレージに保存を試みる
            try {
                const submission = {
                    exercise_type: formData.exercise_id,
                    user_id: userId,
                    submission_date: formData.submitted_at,
                    content: {
                        answers: formData.answers,
                        is_submitted: isSubmitted
                    }
                };
                
                const savedSubmissions = JSON.parse(localStorage.getItem('exercise_submissions') || '[]');
                savedSubmissions.push(submission);
                localStorage.setItem('exercise_submissions', JSON.stringify(savedSubmissions));
                
                console.log('Saved submission to localStorage after error');
                return { data: submission, error: null, source: 'localStorage' };
            } catch (localStorageError) {
                console.error('LocalStorage fallback error:', localStorageError);
                throw new Error('提出中にエラーが発生しました: ' + error.message);
            }
        }
    }
    
    // 保存済みデータの読み込み
    async function loadSavedData() {
        try {
            // Supabaseが初期化されているか確認
            if (!supabaseClient) {
                console.warn('データベース接続が初期化されていません。保存データを読み込めません。');
                return;
            }
            
            // ユーザーIDの取得（匿名ユーザーIDを使用）
            let user;
            try {
                // 匿名サインインが無効なため、ローカルストレージを使用して一貫したユーザーIDを提供
                let userId = localStorage.getItem('anonymous_user_id');
                if (!userId) {
                    // ランダムなユーザーIDを生成して保存
                    userId = 'anon_' + Math.random().toString(36).substring(2, 15) + 
                            Math.random().toString(36).substring(2, 15);
                    localStorage.setItem('anonymous_user_id', userId);
                    console.log('Created new anonymous user ID:', userId);
                    // 新規ユーザーの場合は保存データがないので早期リターン
                    return;
                }
                
                console.log('Using local anonymous user ID for data loading:', userId);
                
                // 匿名ユーザーオブジェクトを作成
                user = {
                    id: userId,
                    email: 'anonymous@example.com',
                    role: 'anonymous'
                };
            } catch (error) {
                console.warn('ユーザーID取得エラー:', error);
                console.warn('ユーザー情報が取得できません。保存データを読み込めません。');
                return;
            }
            
            const exerciseId = exerciseSubmissionForm.dataset.exerciseId;
            
            // 最新の保存データを取得
            const result = await supabaseClient.from('prompt_exercise_submissions')
                .select('*')
                .eq('user_id', user.id)
                .eq('exercise_type', exerciseId)
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
                    new Date(b.submission_date) - new Date(a.submission_date)
                )[0];
                
                // フォームに値を設定
                const answers = latestSubmission.content.answers;
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
    
    // 採点結果表示関数
    function displayGradingResults(results, exerciseType) {
        // 既存の採点結果があれば削除
        const existingResults = document.querySelector('.grading-results');
        if (existingResults) {
            existingResults.remove();
        }
        
        // 採点結果コンテナ作成
        const resultsContainer = document.createElement('div');
        resultsContainer.className = 'grading-results';
        
        // ヘッダー部分（タイトルと総合点）
        const headerHTML = `
            <div class="grading-header">
                <h3 class="grading-title">AI採点結果</h3>
                <div class="overall-score">
                    <div class="score-circle ${results.passed ? 'pass-badge' : 'fail-badge'}">
                        ${results.overallScore}
                    </div>
                    <div class="score-details">
                        <p>10点満点中 ${results.overallScore}点</p>
                        <p>合格ライン: ${results.passingThreshold}点</p>
                        <p>${results.passed ? '合格おめでとうございます！' : '再提出をお勧めします'}</p>
                    </div>
                </div>
            </div>
        `;
        
        // 各質問のフィードバック
        let feedbackHTML = '';
        
        // 質問のタイトルマッピング
        const questionTitles = {
            'chatgpt-basics': {
                'usefulness': 'ChatGPTの法務業務における有用性',
                'accuracy': '回答の正確性と信頼性',
                'effective_prompts': '効果的な質問・指示の出し方',
                'limitations': '法務担当者として認識すべき限界と注意点'
            }
            // 他の演習タイプの質問タイトル
        };
        
        // 各フィードバックを処理
        results.feedbacks.forEach(feedback => {
            const questionTitle = questionTitles[exerciseType] && 
                                questionTitles[exerciseType][feedback.questionId] || 
                                `質問: ${feedback.questionId}`;
            
            feedbackHTML += `
                <div class="question-feedback">
                    <h4 class="question-title">${questionTitle}</h4>
                    
                    <div class="feedback-section positive-feedback">
                        <h4>良かった点</h4>
                        <div class="feedback-content">${feedback.positivePoints}</div>
                    </div>
                    
                    <div class="feedback-section improvement-feedback">
                        <h4>改善すべき点</h4>
                        <div class="feedback-content">${feedback.improvementPoints}</div>
                    </div>
                    
                    <div class="feedback-section goals-feedback">
                        <h4>今後の学習目標</h4>
                        <div class="feedback-content">${feedback.learningGoals}</div>
                    </div>
                </div>
            `;
        });
        
        // 最終的なHTMLをセット
        resultsContainer.innerHTML = headerHTML + feedbackHTML;
        
        // フォームの後に挿入
        exerciseSubmissionForm.after(resultsContainer);
        
        // スクロールして採点結果を表示
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // 採点成功メッセージ
        showMessage('AIによる採点が完了しました。', 'success');
    }
});
