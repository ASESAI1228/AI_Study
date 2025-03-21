/**
 * Supabase クライアント初期化
 * 注意: 実際の実装では、環境変数またはサーバーサイドから安全に取得したキーを使用します
 */

// Supabase接続情報
// 本番環境では環境変数、テスト環境では直接設定された値を使用
const SUPABASE_URL = typeof process !== 'undefined' && process.env && process.env.SUPABASE_URL || 'https://your-supabase-url.supabase.co';
const SUPABASE_KEY = typeof process !== 'undefined' && process.env && process.env.SUPABASE_ANON_KEY || 'your-supabase-anon-key';

// モックモードフラグ（Supabaseへの実際の接続ができない場合にローカルストレージを使用）
let useMockMode = true;

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
                // ダミーユーザー情報を返す
                return { id: 'dummy-user-id', email: 'user@example.com' };
            }
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
        if (SUPABASE_URL !== 'https://your-supabase-url.supabase.co' && 
            SUPABASE_KEY !== 'your-supabase-anon-key') {
            
            // 実際のSupabaseクライアントを初期化
            const client = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
            
            // 接続テスト
            const { error } = await client.from('prompt_exercise_submissions').select('count', { count: 'exact', head: true });
            
            if (error) {
                throw new Error(`Supabase connection test failed: ${error.message}`);
            }
            
            console.log('Supabase client initialized successfully. Using real Supabase.');
            useMockMode = false;
            return client;
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

// ページ読み込み時に Supabase クライアントを初期化
document.addEventListener('DOMContentLoaded', async () => {
    try {
        supabaseClient = await initSupabase();
        console.log('Supabase client ready:', useMockMode ? 'Mock Mode' : 'Real Supabase');
    } catch (error) {
        console.error('Supabase initialization error:', error);
        // エラーが発生した場合もモック実装にフォールバック
        supabaseClient = createMockClient();
    }
});
