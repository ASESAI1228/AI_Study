/**
 * OpenAI API クライアント
 * 課題の自動採点に使用
 */

// 本番環境では環境変数、テスト環境ではハードコードされた値を使用
let OPENAI_API_KEY = '';
let useOpenAIMockMode = false;

try {
  // Validate API key format to prevent URL validation errors
  if (window.OPENAI_API_KEY && typeof window.OPENAI_API_KEY === 'string' && window.OPENAI_API_KEY.startsWith('sk-')) {
    OPENAI_API_KEY = window.OPENAI_API_KEY;
  } else {
    console.warn('Invalid OpenAI API key format. Using mock mode.');
    useOpenAIMockMode = true;
  }
} catch (error) {
  console.error('Error initializing OpenAI credentials:', error);
  useOpenAIMockMode = true;
}

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
        model: 'chatgpt-4o-latest',  // 指定されたモデル名を使用
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
    // プロンプト作成演習1：基本的なプロンプト設計
    'prompt-engineering-ex1': {
      'task1_prompt': {
        description: '契約書の重要条項の抽出と分析のためのプロンプト設計',
        keyPoints: [
          'プロンプトの明確さと具体性',
          '指示の構造化と論理的な順序',
          '出力形式の適切な指定',
          '法的観点からの重要ポイントの指定'
        ]
      },
      'task1_result': {
        description: '契約書分析の実行結果の評価',
        keyPoints: [
          '重要条項の抽出の網羅性',
          '分析の深さと法的洞察',
          '結果の構造化と読みやすさ',
          '実務での活用可能性'
        ]
      },
      'task2_prompt': {
        description: '法的質問への回答のためのプロンプト設計',
        keyPoints: [
          '質問の明確な定義と範囲設定',
          '必要なコンテキスト情報の提供',
          '回答形式の適切な指定',
          'プロンプトの簡潔さと効率性'
        ]
      },
      'task2_result': {
        description: '法的質問への回答結果の評価',
        keyPoints: [
          '回答の法的正確性',
          '説明の明確さと論理性',
          '参考情報や根拠の提示',
          '実務での有用性'
        ]
      },
      'task3_prompt': {
        description: '判例の要約と重要ポイントの抽出のためのプロンプト設計',
        keyPoints: [
          '要約の範囲と焦点の明確な指定',
          '法的観点からの重要ポイント指定',
          '出力形式の構造化',
          'プロンプトの効率性'
        ]
      },
      'task3_result': {
        description: '判例要約の実行結果の評価',
        keyPoints: [
          '要約の簡潔さと完全性',
          '法的重要ポイントの抽出精度',
          '結果の構造と読みやすさ',
          '実務での参照価値'
        ]
      },
      'exercise1_evaluation': {
        description: '結果の評価と改善点の考察',
        keyPoints: [
          '自己評価の客観性と洞察',
          '改善点の具体性と実現可能性',
          'プロンプト設計の原則理解',
          '学習プロセスの反映'
        ]
      }
    },
    // プロンプト作成演習2：プロンプトパターンの適用
    'prompt-engineering-ex2': {
      'role_prompt': {
        description: 'ロールプロンプトパターンの適用',
        keyPoints: [
          'ロール設定の適切さと創造性',
          'ペルソナの一貫性と専門性',
          'タスクに対する適合性',
          '法務分野での実用性'
        ]
      },
      'role_result': {
        description: 'ロールプロンプトの実行結果',
        keyPoints: [
          '指定したロールの反映度',
          '回答の質と専門性',
          '通常のプロンプトとの差異',
          '法務業務での有用性'
        ]
      },
      'step_prompt': {
        description: 'ステップバイステップ指示パターンの適用',
        keyPoints: [
          'ステップの論理的順序と明確さ',
          '各ステップの具体性と実行可能性',
          'プロセス全体の完全性',
          '法務タスクへの適合性'
        ]
      },
      'step_result': {
        description: 'ステップバイステップ指示の実行結果',
        keyPoints: [
          '指示に従った段階的な回答',
          '各ステップの完成度',
          '全体としての一貫性と完全性',
          '法的分析の質'
        ]
      },
      'few_shot_prompt': {
        description: 'フューショット学習パターンの適用',
        keyPoints: [
          '例示の適切さと代表性',
          '例示の数と多様性',
          'タスクとの関連性',
          '法務コンテキストでの適切性'
        ]
      },
      'few_shot_result': {
        description: 'フューショット学習の実行結果',
        keyPoints: [
          '例示パターンの学習度',
          '回答の一貫性と品質',
          '例示なしの場合との比較',
          '法的文脈での正確性'
        ]
      },
      'pattern_analysis': {
        description: 'パターン適用の効果分析',
        keyPoints: [
          '各パターンの効果の比較分析',
          '法務タスクに最適なパターンの識別',
          '分析の深さと洞察',
          '実務への応用提案'
        ]
      }
    },
    // プロンプト作成演習3：プロンプトの反復的改善
    'prompt-engineering-ex3': {
      'initial_prompt': {
        description: '初期プロンプトの設計',
        keyPoints: [
          'プロンプトの基本構造と明確さ',
          'タスクの定義と範囲設定',
          '法務コンテキストの適切な設定',
          '改善の余地の認識'
        ]
      },
      'initial_result': {
        description: '初期プロンプトの実行結果',
        keyPoints: [
          '回答の基本的な質と関連性',
          '不足点や改善点の識別',
          '法的内容の正確性',
          '結果の構造と使いやすさ'
        ]
      },
      'improved_prompt': {
        description: '改善したプロンプトの設計',
        keyPoints: [
          '初期プロンプトからの具体的改善点',
          '指示の明確化と詳細化',
          '出力形式の最適化',
          '法的観点の強化'
        ]
      },
      'improved_result': {
        description: '改善プロンプトの実行結果',
        keyPoints: [
          '初期結果からの改善度',
          '回答の質と完全性の向上',
          '法的分析の深化',
          '実用性の向上'
        ]
      },
      'final_prompt': {
        description: '最終プロンプトの設計',
        keyPoints: [
          '反復プロセスを通じた最適化',
          'プロンプト設計の原則の適用',
          '法務タスクに特化した調整',
          '効率性と効果のバランス'
        ]
      },
      'final_result': {
        description: '最終プロンプトの実行結果',
        keyPoints: [
          '初期および改善版との比較',
          '法的分析の質と深さ',
          '実務での直接的な有用性',
          '目標達成度'
        ]
      },
      'improvement_process': {
        description: '改善プロセスの説明と学んだ教訓',
        keyPoints: [
          'プロンプト改善の体系的アプローチ',
          '各改善ステップの効果分析',
          '法務プロンプト設計の原則抽出',
          '今後の応用への洞察'
        ]
      }
    },
    // プロンプト作成演習4：実務向けプロンプトライブラリの作成
    'prompt-engineering-ex4': {
      'template1': {
        description: 'プロンプトテンプレート1の設計',
        keyPoints: [
          'テンプレートの明確さと汎用性',
          '法務業務での具体的用途',
          'カスタマイズ可能な要素',
          '実務での効率性'
        ]
      },
      'template1_purpose': {
        description: 'テンプレート1の使用目的と適用シナリオ',
        keyPoints: [
          '使用目的の明確な定義',
          '適用シナリオの具体性と現実性',
          '法務業務での価値提案',
          '使用方法の明確な説明'
        ]
      },
      'template2': {
        description: 'プロンプトテンプレート2の設計',
        keyPoints: [
          'テンプレートの明確さと汎用性',
          '法務業務での具体的用途',
          'カスタマイズ可能な要素',
          '実務での効率性'
        ]
      },
      'template2_purpose': {
        description: 'テンプレート2の使用目的と適用シナリオ',
        keyPoints: [
          '使用目的の明確な定義',
          '適用シナリオの具体性と現実性',
          '法務業務での価値提案',
          '使用方法の明確な説明'
        ]
      },
      'template3': {
        description: 'プロンプトテンプレート3の設計',
        keyPoints: [
          'テンプレートの明確さと汎用性',
          '法務業務での具体的用途',
          'カスタマイズ可能な要素',
          '実務での効率性'
        ]
      },
      'template3_purpose': {
        description: 'テンプレート3の使用目的と適用シナリオ',
        keyPoints: [
          '使用目的の明確な定義',
          '適用シナリオの具体性と現実性',
          '法務業務での価値提案',
          '使用方法の明確な説明'
        ]
      },
      'template4': {
        description: 'プロンプトテンプレート4の設計',
        keyPoints: [
          'テンプレートの明確さと汎用性',
          '法務業務での具体的用途',
          'カスタマイズ可能な要素',
          '実務での効率性'
        ]
      },
      'template4_purpose': {
        description: 'テンプレート4の使用目的と適用シナリオ',
        keyPoints: [
          '使用目的の明確な定義',
          '適用シナリオの具体性と現実性',
          '法務業務での価値提案',
          '使用方法の明確な説明'
        ]
      },
      'template5': {
        description: 'プロンプトテンプレート5の設計',
        keyPoints: [
          'テンプレートの明確さと汎用性',
          '法務業務での具体的用途',
          'カスタマイズ可能な要素',
          '実務での効率性'
        ]
      },
      'template5_purpose': {
        description: 'テンプレート5の使用目的と適用シナリオ',
        keyPoints: [
          '使用目的の明確な定義',
          '適用シナリオの具体性と現実性',
          '法務業務での価値提案',
          '使用方法の明確な説明'
        ]
      },
      'library_usage': {
        description: 'ライブラリの活用方法の説明',
        keyPoints: [
          'ライブラリ全体の構成と論理',
          'テンプレート選択の指針',
          'カスタマイズと拡張方法',
          '法務業務での効果的な統合'
        ]
      }
    }
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
