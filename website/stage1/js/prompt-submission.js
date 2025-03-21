/**
 * プロンプト演習提出フォーム用のJavaScript
 */

document.addEventListener('DOMContentLoaded', async () => {
    // フォーム要素の参照を取得
    const exerciseForm = document.getElementById('prompt-exercise-form');
    const exerciseSelect = document.getElementById('exercise-select');
    const formSections = document.querySelectorAll('.exercise-form-section');
    const submitButton = document.getElementById('submit-exercise');
    const statusMessage = document.getElementById('submission-status');

    // 初期表示時は最初の演習フォームのみ表示
    if (formSections.length > 0) {
        showSelectedExercise('exercise1');
    }

    // 演習選択時の処理
    if (exerciseSelect) {
        exerciseSelect.addEventListener('change', (e) => {
            const selectedExercise = e.target.value;
            showSelectedExercise(selectedExercise);
        });
    }

    // 選択された演習フォームのみを表示する関数
    function showSelectedExercise(exerciseId) {
        formSections.forEach(section => {
            if (section.id === exerciseId + '-section') {
                section.style.display = 'block';
            } else {
                section.style.display = 'none';
            }
        });
    }

    // フォーム送信処理
    if (exerciseForm) {
        exerciseForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // 送信中の状態表示
            submitButton.disabled = true;
            statusMessage.textContent = '送信中...';
            statusMessage.className = 'status-message info';
            
            try {
                // フォームデータの収集
                const formData = new FormData(exerciseForm);
                const selectedExercise = exerciseSelect.value;
                
                // 送信データの作成
                let user;
                try {
                    const { data } = await supabaseClient.auth.getUser();
                    user = data.user;
                } catch (error) {
                    throw new Error('ユーザー情報が取得できません: ' + error.message);
                }

                const submissionData = {
                    exercise_type: selectedExercise,
                    user_id: user ? user.id : 'anonymous',
                    submission_date: new Date().toISOString(),
                    content: {}
                };
                
                // 選択された演習に応じたデータ構造を作成
                switch (selectedExercise) {
                    case 'exercise1':
                        submissionData.content = {
                            task1_prompt: formData.get('task1_prompt'),
                            task1_result: formData.get('task1_result'),
                            task2_prompt: formData.get('task2_prompt'),
                            task2_result: formData.get('task2_result'),
                            task3_prompt: formData.get('task3_prompt'),
                            task3_result: formData.get('task3_result'),
                            evaluation: formData.get('exercise1_evaluation')
                        };
                        break;
                    case 'exercise2':
                        submissionData.content = {
                            role_prompt: formData.get('role_prompt'),
                            role_result: formData.get('role_result'),
                            step_prompt: formData.get('step_prompt'),
                            step_result: formData.get('step_result'),
                            few_shot_prompt: formData.get('few_shot_prompt'),
                            few_shot_result: formData.get('few_shot_result'),
                            pattern_analysis: formData.get('pattern_analysis')
                        };
                        break;
                    case 'exercise3':
                        submissionData.content = {
                            initial_prompt: formData.get('initial_prompt'),
                            initial_result: formData.get('initial_result'),
                            improved_prompt: formData.get('improved_prompt'),
                            improved_result: formData.get('improved_result'),
                            final_prompt: formData.get('final_prompt'),
                            final_result: formData.get('final_result'),
                            improvement_process: formData.get('improvement_process')
                        };
                        break;
                    case 'exercise4':
                        submissionData.content = {
                            template1: {
                                purpose: formData.get('template1_purpose'),
                                prompt: formData.get('template1_prompt'),
                                input_info: formData.get('template1_input'),
                                output_format: formData.get('template1_output'),
                                notes: formData.get('template1_notes')
                            },
                            template2: {
                                purpose: formData.get('template2_purpose'),
                                prompt: formData.get('template2_prompt'),
                                input_info: formData.get('template2_input'),
                                output_format: formData.get('template2_output'),
                                notes: formData.get('template2_notes')
                            },
                            template3: {
                                purpose: formData.get('template3_purpose'),
                                prompt: formData.get('template3_prompt'),
                                input_info: formData.get('template3_input'),
                                output_format: formData.get('template3_output'),
                                notes: formData.get('template3_notes')
                            },
                            template4: {
                                purpose: formData.get('template4_purpose'),
                                prompt: formData.get('template4_prompt'),
                                input_info: formData.get('template4_input'),
                                output_format: formData.get('template4_output'),
                                notes: formData.get('template4_notes')
                            },
                            template5: {
                                purpose: formData.get('template5_purpose'),
                                prompt: formData.get('template5_prompt'),
                                input_info: formData.get('template5_input'),
                                output_format: formData.get('template5_output'),
                                notes: formData.get('template5_notes')
                            },
                            library_usage: formData.get('library_usage')
                        };
                        break;
                }
                
                // Supabaseに送信
                const { data, error } = await supabaseClient
                    .from('prompt_exercise_submissions')
                    .insert(submissionData);
                
                if (error) {
                    throw new Error(error.message);
                }
                
                // 送信成功時の処理
                statusMessage.textContent = '提出が完了しました！';
                statusMessage.className = 'status-message success';
                
                // フォームをリセット
                exerciseForm.reset();
                
            } catch (error) {
                console.error('提出エラー:', error);
                statusMessage.textContent = 'エラーが発生しました: ' + error.message;
                statusMessage.className = 'status-message error';
            } finally {
                submitButton.disabled = false;
            }
        });
    }
});
