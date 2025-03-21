/**
 * OpenAI API クライアント
 * 課題の自動採点に使用
 */

// 本番環境では環境変数、テスト環境ではハードコードされた値を使用
const OPENAI_API_KEY = window.OPENAI_API_KEY || 'sk-your-test-api-key';

// モックモードフラグ（OpenAI APIが利用できない場合）
let useOpenAIMockMode = false;

// グローバル変数としてOpenAIクライアントを保持
let openaiClient = null;

/**
 * OpenAIクライアントの初期化
 */
async function initOpenAI() {
  console.log('Initializing OpenAI client...');
  
  try {
    // APIキーが有効か確認
    if (OPENAI_API_KEY && OPENAI_API_KEY.startsWith('sk-') && OPENAI_API_KEY.length > 20) {
      console.log('Valid OpenAI API key found');
      useOpenAIMockMode = false;
      return {
        createGradingAssessment: createRealGradingAssessment
      };
    } else {
      throw new Error('Invalid OpenAI API key');
    }
  } catch (error) {
    console.warn(`Failed to initialize OpenAI client: ${error.message}. Falling back to mock implementation.`);
    useOpenAIMockMode = true;
    
    // モック実装を返す
    return {
      createGradingAssessment: createMockGradingAssessment
    };
  }
}

/**
 * 実際のOpenAI APIを使用して採点を実行
 */
async function createRealGradingAssessment(exerciseType, answers, updateProgress) {
  try {
    // 進捗状況を更新（0%）
    updateProgress && updateProgress(0, '採点を開始しています...');
    
    // 各質問の採点基準を取得
    const criterias = getGradingCriterias(exerciseType);
    
    // 進捗状況を更新（20%）
    updateProgress && updateProgress(20, '採点基準を準備しています...');
    
    // 採点するための質問と回答をフォーマット
    const formattedQuestions = formatQuestionsForGrading(exerciseType, answers, criterias);
    
    // 進捗状況を更新（40%）
    updateProgress && updateProgress(40, 'AIに採点を依頼しています...');
    
    // OpenAI APIに採点リクエストを送信
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENAI_API_KEY}`
      },
      body: JSON.stringify({
        model: 'gpt-4o-latest',
        messages: [
          { 
            role: 'system', 
            content: '採点者として、学生の回答を採点し、10点満点でスコアを評価してください。回答は厳格かつ公平に評価し、良かった点、改善すべき点、今後の学習目標を記載してください。' 
          },
          { role: 'user', content: formattedQuestions }
        ],
        temperature: 0.3,
        response_format: { type: 'json_object' }
      })
    });
    
    // 進捗状況を更新（70%）
    updateProgress && updateProgress(70, 'AIからのフィードバックを処理しています...');
    
    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }
    
    const responseData = await response.json();
    const gradingResult = JSON.parse(responseData.choices[0].message.content);
    
    // 進捗状況を更新（100%）
    updateProgress && updateProgress(100, '採点が完了しました');
    
    return formatGradingResults(gradingResult);
  } catch (error) {
    console.error('OpenAI grading error:', error);
    throw new Error(`採点中にエラーが発生しました: ${error.message}`);
  }
}

/**
 * モック実装（開発・テスト用）
 */
async function createMockGradingAssessment(exerciseType, answers, updateProgress) {
  return new Promise((resolve) => {
    // 進捗シミュレーション
    updateProgress && updateProgress(0, '採点を開始しています...');
    
    setTimeout(() => updateProgress && updateProgress(25, '採点基準を準備しています...'), 500);
    setTimeout(() => updateProgress && updateProgress(50, 'AIに採点を依頼しています...'), 1000);
    setTimeout(() => updateProgress && updateProgress(75, 'AIからのフィードバックを処理しています...'), 1500);
    
    setTimeout(() => {
      updateProgress && updateProgress(100, '採点が完了しました');
      
      // モック採点結果を返す
      resolve({
        overallScore: 8,
        passingThreshold: 6,
        passed: true,
        feedbacks: [
          {
            questionId: Object.keys(answers)[0],
            score: 8,
            positivePoints: 'モック回答のポジティブなフィードバック。実際の回答を考慮した的確な指摘がここに表示されます。',
            improvementPoints: '改善すべき点として、より具体的な例を挙げると良いでしょう。',
            learningGoals: '今後の学習目標として、この分野の最新動向を把握することをお勧めします。'
          },
          // 他の質問のフィードバック
        ]
      });
    }, 2000);
  });
}

/**
 * 採点基準の定義
 */
function getGradingCriterias(exerciseType) {
  const criterias = {
    'chatgpt-basics': {
      'usefulness': {
        description: 'ChatGPTが法務業務においてどのように役立つか、具体的な例を挙げて説明',
        keyPoints: [
          '法務業務での具体的なユースケース',
          '実際の業務効率化への貢献',
          '法的文書作成や分析における有用性',
          '具体例の適切さと現実性'
        ]
      },
      'accuracy': {
        description: 'ChatGPTの回答の正確性と信頼性の評価',
        keyPoints: [
          '法的正確性の限界の理解',
          '情報の信頼性に対する批判的視点',
          '具体的な評価基準の提示',
          '実例に基づく分析'
        ]
      },
      'effective_prompts': {
        description: '効果的な質問や指示の出し方についての発見',
        keyPoints: [
          'プロンプト設計の具体的テクニック',
          '質問の明確さと具体性の重要性理解',
          '効果的なプロンプトの例示',
          '実践的な改善方法の提案'
        ]
      },
      'limitations': {
        description: '法務担当者がChatGPTを活用する際の限界と注意点',
        keyPoints: [
          '法的責任や倫理的考慮の言及',
          'AIの限界についての適切な理解',
          '法的リスクへの認識',
          '適切な利用範囲の提案'
        ]
      }
    },
    // 他の演習タイプの採点基準
  };
  
  return criterias[exerciseType] || {};
}

/**
 * APIリクエスト用に質問と回答をフォーマット
 */
function formatQuestionsForGrading(exerciseType, answers, criterias) {
  let formattedText = `課題種別: ${exerciseType}\n\n`;
  
  for (const questionId in answers) {
    if (criterias[questionId]) {
      formattedText += `質問: ${criterias[questionId].description}\n`;
      formattedText += `評価ポイント: ${criterias[questionId].keyPoints.join(', ')}\n`;
      formattedText += `回答: ${answers[questionId]}\n\n`;
    }
  }
  
  formattedText += `
以下のJSON形式で各質問への採点結果を返してください：
{
  "overallScore": 数値（10点満点）,
  "feedbacks": [
    {
      "questionId": "質問ID",
      "score": 数値（10点満点）,
      "positivePoints": "良かった点（具体的に）",
      "improvementPoints": "改善すべき点（具体的に）",
      "learningGoals": "今後の学習目標の提案"
    },
    ...他の質問
  ]
}`;
  
  return formattedText;
}

/**
 * APIレスポンスを整形
 */
function formatGradingResults(apiResponse) {
  // 合格基準（6点）を追加
  const passingThreshold = 6;
  
  return {
    overallScore: apiResponse.overallScore,
    passingThreshold: passingThreshold,
    passed: apiResponse.overallScore >= passingThreshold,
    feedbacks: apiResponse.feedbacks
  };
}

// ページ読み込み時にOpenAIクライアントを初期化
document.addEventListener('DOMContentLoaded', async () => {
  try {
    openaiClient = await initOpenAI();
    console.log('OpenAI client ready:', useOpenAIMockMode ? 'Mock Mode' : 'Real API');
  } catch (error) {
    console.error('OpenAI initialization error:', error);
  }
});
