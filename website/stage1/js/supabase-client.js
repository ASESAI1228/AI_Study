/**
 * Supabase クライアント初期化
 * 注意: 実際の実装では、環境変数またはサーバーサイドから安全に取得したキーを使用します
 */

// Supabase接続情報
// 本番環境では環境変数、テスト環境では直接設定された値を使用
const SUPABASE_URL = window.SUPABASE___SUPABASE_URL || 'https://your-supabase-url.supabase.co';
const SUPABASE_KEY = window.SUPABASE___SUPABASE_ANON_KEY || 'your-supabase-anon-key';

// モックモードフラグ（Supabaseへの実際の接続ができない場合にローカルストレージを使用）
let useMockMode = false;

/**
 * モッククライアントを作成する関数
 * Supabase接続が利用できない場合のフォールバック
 */
function createMockClient() {
    console.log('Creating mock Supabase client with localStorage');
    
    return {
        from: (table) => ({
            insert: (data) => {
                console.log(`[Mock] Inserting data into ${table}:`, data);
                return {
                    then: (callback) => {
                        // ローカルストレージに保存（デモ用）
                        const storageKey = `supabase_${table}_data`;
                        const existingData = JSON.parse(localStorage.getItem(storageKey) || '[]');
                        existingData.push({...data, id: Date.now(), created_at: new Date().toISOString()});
                        localStorage.setItem(storageKey, JSON.stringify(existingData));
                        
                        callback({ data: data, error: null });
                        return {
                            catch: (errorCallback) => {
                                // エラーハンドリング
                                return Promise.resolve({ data, error: null });
                            }
                        };
                    }
                };
            },
            select: (columns) => {
                console.log(`[Mock] Selecting ${columns} from ${table}`);
                return {
                    eq: (column, value) => {
                        console.log(`[Mock] Where ${column} = ${value}`);
                        return {
                            then: (callback) => {
                                // ローカルストレージから取得（デモ用）
                                const storageKey = `supabase_${table}_data`;
                                const allData = JSON.parse(localStorage.getItem(storageKey) || '[]');
                                const filteredData = allData.filter(item => item[column] === value);
                                
                                callback({ data: filteredData, error: null });
                                return {
                                    catch: (errorCallback) => {
                                        // エラーハンドリング
                                        return Promise.resolve({ data: filteredData, error: null });
                                    }
                                };
                            }
                        };
                    }
                };
            }
        }),
        auth: {
            user: () => {
                // ダミーユーザー情報を返す（旧APIとの互換性のため）
                return { id: 'dummy-user-id', email: 'user@example.com' };
            },
            getUser: () => {
                console.log('[Mock] Getting user information');
                // 常に成功するダミーユーザーを返す
                return Promise.resolve({
                    data: {
                        user: { id: 'dummy-user-id', email: 'user@example.com' }
                    },
                    error: null
                });
            },
            getSession: () => {
                console.log('[Mock] Getting session information');
                // セッション情報も同様に実装
                return Promise.resolve({
                    data: {
                        session: { 
                            user: { id: 'dummy-user-id', email: 'user@example.com' },
                            expires_at: Date.now() + 3600
                        }
                    },
                    error: null
                });
            }
        },
        saveGradingResults: (data) => {
            console.log('[Mock] Saving grading results:', data);
            // モック実装でローカルストレージに保存
            const storageKey = 'mock_grading_results';
            const existingData = JSON.parse(localStorage.getItem(storageKey) || '[]');
            const resultWithId = {
                ...data,
                id: Date.now(),
                created_at: new Date().toISOString()
            };
            existingData.push(resultWithId);
            localStorage.setItem(storageKey, JSON.stringify(existingData));
            return Promise.resolve({ data: resultWithId, error: null });
        }
    };
}

/**
 * Supabase クライアントを初期化する関数
 * 実際のSupabaseクライアントを初期化し、失敗した場合はモック実装にフォールバック
 */
async function initSupabase() {
    console.log('Initializing Supabase client...');
    
    try {
        // Supabase URLとキーが有効な値か確認
        if (SUPABASE_URL && SUPABASE_URL.includes('supabase.co') && 
            SUPABASE_KEY && SUPABASE_KEY.length > 20) {
            
            // 実際のSupabaseクライアントを初期化
            const client = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
            
            // 接続テスト - より柔軟なチェック
            try {
                // auth接続のテスト（テーブル存在チェックの代わり）
                const { data, error } = await client.auth.getSession();
                
                if (error) {
                    throw new Error(`Supabase auth connection test failed: ${error.message}`);
                }
                
                console.log('Supabase client initialized successfully. Using real Supabase.');
                useMockMode = false;
                return client;
            } catch (connError) {
                console.warn(`Supabase connection test failed: ${connError.message}`);
                throw connError;
            }
        } else {
            throw new Error('Invalid Supabase credentials');
        }
    } catch (error) {
        console.warn(`Failed to initialize Supabase client: ${error.message}. Falling back to mock implementation.`);
        useMockMode = true;
        
        // モック実装を返す
        return createMockClient();
    }
}

// グローバル変数として supabase クライアントを保持
let supabaseClient = null;

/**
 * ユーザーIDを取得する関数
 * 認証済みユーザーまたは匿名ユーザーID
 * @returns {Promise<string>} ユーザーID
 */
async function getUserId() {
    try {
        if (useMockMode) {
            // モックモード: ローカルストレージのIDを返す
            let userId = localStorage.getItem('anonymous_user_id');
            if (!userId) {
                userId = 'anon_' + Math.random().toString(36).substring(2, 15);
                localStorage.setItem('anonymous_user_id', userId);
            }
            return userId;
        } else {
            // 実際のSupabaseから取得
            const { data } = await supabase.auth.getUser();
            return data && data.user ? data.user.id : null;
        }
    } catch (error) {
        console.error('Failed to get user ID:', error);
        throw error;
    }
}

/**
 * 課題提出を保存する関数
 * @param {Object} submissionData - 提出データ
 * @returns {Promise<Object>} - 保存結果
 */
async function saveSubmission(submissionData) {
    console.log('Saving submission:', submissionData);
    
    try {
        if (useMockMode) {
            // モックモード: ローカルストレージに保存
            const submissionId = 'submission_' + Date.now();
            const submission = {
                id: submissionId,
                ...submissionData,
                created_at: new Date().toISOString()
            };
            
            localStorage.setItem(`submission_${submissionId}`, JSON.stringify(submission));
            return { data: submission, error: null };
        } else {
            // 実際のSupabaseに保存
            const { data, error } = await supabase
                .from('prompt_exercise_submissions')
                .insert(submissionData)
                .select()
                .single();
            
            return { data, error };
        }
    } catch (error) {
        console.error('Error saving submission:', error);
        return { data: null, error };
    }
}

/**
 * 大きな提出データのチャンクを保存する関数
 * @param {Object} chunkData - チャンクデータ
 * @returns {Promise<Object>} - 保存結果
 */
async function saveSubmissionChunk(chunkData) {
    console.log('Saving submission chunk:', chunkData);
    
    try {
        if (useMockMode) {
            // モックモード: ローカルストレージに保存
            const chunkId = `chunk_${chunkData.submission_id}_${chunkData.chunk_index}`;
            localStorage.setItem(chunkId, JSON.stringify(chunkData));
            return { data: chunkData, error: null };
        } else {
            // 実際のSupabaseに保存
            const { data, error } = await supabase
                .from('prompt_exercise_submission_chunks')
                .insert(chunkData)
                .select();
            
            return { data, error };
        }
    } catch (error) {
        console.error('Error saving submission chunk:', error);
        return { data: null, error };
    }
}

/**
 * 採点結果を保存する関数
 * @param {Object} data - 保存するデータ
 * @param {string} data.submission_id - 提出ID
 * @param {Object} data.grading_results - 採点結果
 * @returns {Promise<Object>} - 保存結果
 */
async function saveGradingResults(data) {
    console.log('Saving grading results:', data);
    
    try {
        if (useMockMode) {
            // モックモード: ローカルストレージに保存
            const storageKey = 'supabase_grading_results';
            const existingData = JSON.parse(localStorage.getItem(storageKey) || '[]');
            const resultWithId = {
                ...data,
                id: Date.now(),
                created_at: new Date().toISOString()
            };
            existingData.push(resultWithId);
            localStorage.setItem(storageKey, JSON.stringify(existingData));
            return { data: resultWithId, error: null };
        } else {
            // 実際のSupabaseに保存
            const { data: result, error } = await supabase
                .from('exercise_grading_results')
                .insert({
                    submission_id: data.submission_id,
                    score: data.grading_results.overallScore,
                    passing_threshold: data.grading_results.passingThreshold,
                    passed: data.grading_results.passed,
                    feedback: data.grading_results.feedbacks,
                    created_at: new Date().toISOString()
                });
            
            return { data: result, error };
        }
    } catch (error) {
        console.error('Error saving grading results:', error);
        return { data: null, error };
    }
}

// ページ読み込み時に Supabase クライアントを初期化
document.addEventListener('DOMContentLoaded', async () => {
    try {
        console.log('Supabase URL:', SUPABASE_URL.substring(0, 15) + '...');
        console.log('Supabase Key:', SUPABASE_KEY.substring(0, 5) + '...' + SUPABASE_KEY.substring(SUPABASE_KEY.length - 5));
        
        supabaseClient = await initSupabase();
        console.log('Supabase client ready:', useMockMode ? 'Mock Mode' : 'Real Supabase');
        
        // クライアントにメソッドを追加
        supabaseClient.getUserId = async function() {
            return getUserId();
        };
        
        supabaseClient.saveSubmission = async function(data) {
            return saveSubmission(data);
        };
        
        supabaseClient.saveSubmissionChunk = async function(data) {
            return saveSubmissionChunk(data);
        };
        
        supabaseClient.saveGradingResults = async function(data) {
            return saveGradingResults(data);
        };
        
        if (!useMockMode) {
            // 実際のクライアントで認証テスト
            try {
                const { data } = await supabaseClient.auth.getUser();
                console.log('Auth test successful:', data.user ? 'User found' : 'No user (anonymous)');
            } catch (authError) {
                console.error('Auth test failed:', authError);
            }
        }
    } catch (error) {
        console.error('Supabase initialization error:', error);
        // エラーが発生した場合もモック実装にフォールバック
        supabaseClient = createMockClient();
        
        // モッククライアントにもメソッドを追加
        supabaseClient.getUserId = async function() {
            return getUserId();
        };
        
        supabaseClient.saveSubmission = async function(data) {
            return saveSubmission(data);
        };
        
        supabaseClient.saveSubmissionChunk = async function(data) {
            return saveSubmissionChunk(data);
        };
        
        supabaseClient.saveGradingResults = async function(data) {
            return saveGradingResults(data);
        };
    }
});
