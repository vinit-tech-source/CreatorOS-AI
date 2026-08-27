import { useState, useEffect, useRef } from 'react';
import { PlatformConfig, ContentFormat } from '../../../constants/platformConfigs';
import { StudioState, CanvasElement } from '../CreateStudio';
import { Sparkles, ArrowRight, ChevronRight, Check, Pencil, Wand2, Loader2, MessageSquarePlus, RotateCcw, ImagePlus, Link, MapPin, X, ArrowLeft } from 'lucide-react';
import styles from './AICreationFlow.module.css';

interface AICreationFlowProps {
  platformConfig: PlatformConfig;
  format: ContentFormat;
  state: StudioState;
  onComplete: (result: AIResult) => void;
  onSkip: () => void;
  onBack?: () => void;
}

export interface AIResult {
  caption: string;
  title: string;
  hashtags: string[];
  elements: Omit<CanvasElement, 'id' | 'zIndex'>[];
}

// Platform-specific questions tailored per format
function getQuestions(_platform: string, formatLabel: string, _concept: string): Question[] {
  const isVideo = ['reel', 'video', 'short', 'tiktok-video', 'story'].some(v => formatLabel.toLowerCase().includes(v));

  return [
    {
      id: 'audience',
      question: `Who is your target audience for this ${formatLabel.toLowerCase()}?`,
      placeholder: 'e.g., Young entrepreneurs aged 18–30, fitness enthusiasts, tech beginners…',
      hint: 'Being specific helps tailor the tone and language of your content.',
    },
    {
      id: 'tone',
      question: 'What tone or style should the content have?',
      placeholder: 'e.g., Inspirational & motivating, Funny & casual, Professional & authoritative…',
      hint: 'Your tone defines how viewers connect with your message.',
      options: ['Inspirational', 'Educational', 'Entertaining', 'Professional', 'Casual & Friendly', 'Bold & Direct'],
    },
    {
      id: 'goal',
      question: 'What is the main goal of this content?',
      placeholder: 'e.g., Get more followers, Promote a product, Drive website traffic, Build trust…',
      hint: 'A clear goal shapes the call-to-action and content structure.',
      options: ['Grow followers', 'Promote a product/service', 'Educate my audience', 'Go viral', 'Build brand trust', 'Drive traffic'],
    },
    {
      id: 'hook',
      question: isVideo
        ? 'How should the content open to grab attention in the first 3 seconds?'
        : 'What should be the first line or hook that grabs attention?',
      placeholder: isVideo
        ? 'e.g., Start with a shocking fact, a bold question, or a dramatic visual…'
        : 'e.g., Start with a powerful quote, a surprising question, or a bold statement…',
      hint: 'The hook determines whether viewers stop scrolling or keep going.',
    },
    {
      id: 'cta',
      question: 'What should viewers do after consuming this content?',
      placeholder: 'e.g., Follow for more, Comment your thoughts, Visit the link in bio, Share with a friend…',
      hint: 'Every great piece of content ends with a clear next step.',
      options: ['Follow for more', 'Comment below', 'Share with friends', 'Visit link in bio', 'Save this post', 'DM me'],
    },
  ];
}

interface Question {
  id: string;
  question: string;
  placeholder: string;
  hint: string;
  options?: string[];
}

type FlowStep = 'prompt' | 'questions' | 'generating' | 'result';

const generationSteps = [
  { label: 'Understanding your concept…', icon: '🧠' },
  { label: 'Researching trends & best practices…', icon: '📊' },
  { label: 'Crafting your caption & hook…', icon: '✍️' },
  { label: 'Selecting hashtags for maximum reach…', icon: '#️⃣' },
  { label: 'Building your visual layout…', icon: '🎨' },
];

export function AICreationFlow({ platformConfig, format, onComplete, onSkip, onBack }: AICreationFlowProps) {
  const [flowStep, setFlowStep] = useState<FlowStep>('prompt');
  const [concept, setConcept] = useState('');
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [generationStep, setGenerationStep] = useState(0);
  const [result, setResult] = useState<AIResult | null>(null);
  const [editPrompt, setEditPrompt] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  
  const [mediaFiles, setMediaFiles] = useState<File[]>([]);
  const [postLink, setPostLink] = useState('');
  const [postLocation, setPostLocation] = useState('');
  const [showLinkInput, setShowLinkInput] = useState(false);
  const [showLocationInput, setShowLocationInput] = useState(false);
  
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setMediaFiles(prev => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const removeFile = (index: number) => {
    setMediaFiles(prev => prev.filter((_, i) => i !== index));
  };

  const questions = getQuestions(platformConfig.name, format.label, concept);

  // Auto-focus input on step change
  useEffect(() => {
    if (flowStep === 'prompt' || flowStep === 'questions') {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [flowStep, currentQ]);

  const handleConceptSubmit = () => {
    if (!concept.trim()) return;
    setFlowStep('questions');
    setCurrentQ(0);
    setCurrentAnswer('');
  };

  const handleAnswerSubmit = () => {
    const q = questions[currentQ];
    const updatedAnswers = { ...answers, [q.id]: currentAnswer || 'Not specified' };
    setAnswers(updatedAnswers);
    setCurrentAnswer('');

    if (currentQ < questions.length - 1) {
      setCurrentQ(prev => prev + 1);
    } else {
      // All questions answered — start generating
      startGeneration(updatedAnswers);
    }
  };

  const startGeneration = async (finalAnswers: Record<string, string>) => {
    setFlowStep('generating');
    setGenerationStep(0);

    // Simulate progressive generation steps
    for (let i = 0; i < generationSteps.length; i++) {
      await new Promise(res => setTimeout(res, 900 + Math.random() * 400));
      setGenerationStep(i + 1);
    }

    // Generate a realistic AI result based on answers
    const tone = finalAnswers.tone || 'Professional';
    const goal = finalAnswers.goal || 'Grow followers';
    const cta = finalAnswers.cta || 'Follow for more';
    const audience = finalAnswers.audience || 'general audience';
    const hook = finalAnswers.hook || '';

    const hookLine = hook
      ? hook.length < 80 ? hook : hook.slice(0, 80) + '…'
      : `Did you know that ${concept.split(' ').slice(0, 4).join(' ')} changes everything?`;

    const caption = `${hookLine}\n\n${concept}\n\nCreated for ${audience} with a ${tone.toLowerCase()} voice — designed to ${goal.toLowerCase()}.\n\n${cta} 👇`;

    const hashtags = generateHashtags(platformConfig.name, concept, tone);

    const elements: Omit<CanvasElement, 'id' | 'zIndex'>[] = [
      {
        type: 'text',
        x: 40,
        y: 50,
        w: format.canvasW - 80,
        h: 80,
        content: hookLine,
        fontSize: 30,
        color: '#ffffff',
        fontWeight: '800',
        textAlign: 'center',
      },
      {
        type: 'text',
        x: 40,
        y: 160,
        w: format.canvasW - 80,
        h: 50,
        content: concept,
        fontSize: 18,
        color: 'rgba(255,255,255,0.75)',
        fontWeight: '500',
        textAlign: 'center',
      },
      {
        type: 'shape',
        x: format.canvasW / 2 - 60,
        y: format.canvasH - 90,
        w: 120,
        h: 40,
        backgroundColor: platformConfig.accentColor,
        borderRadius: 20,
      },
      {
        type: 'text',
        x: format.canvasW / 2 - 60,
        y: format.canvasH - 87,
        w: 120,
        h: 36,
        content: cta,
        fontSize: 13,
        color: '#ffffff',
        fontWeight: '700',
        textAlign: 'center',
      },
    ];

    const generated: AIResult = { caption, title: hookLine, hashtags, elements };
    setResult(generated);
    setFlowStep('result');
  };

  const handleEditWithPrompt = async () => {
    if (!editPrompt.trim() || !result) return;
    setIsEditing(true);
    await new Promise(res => setTimeout(res, 1500));

    // Simulate AI applying the edit
    const updatedCaption = result.caption + `\n\n✨ ${editPrompt}`;
    setResult({ ...result, caption: updatedCaption });
    setEditPrompt('');
    setIsEditing(false);
  };

  const handleAccept = () => {
    if (result) onComplete(result);
  };

  const handleManualEdit = () => {
    if (result) onComplete(result);
  };

  const handleReset = () => {
    setConcept('');
    setAnswers({});
    setCurrentAnswer('');
    setCurrentQ(0);
    setResult(null);
    setFlowStep('prompt');
  };

  return (
    <div className={styles.overlay}>
      {/* Animated bg */}
      <div className={styles.bgGlow} style={{ 
        backgroundImage: `radial-gradient(circle at 15% 50%, ${platformConfig.accentColor}25, transparent 55%), radial-gradient(circle at 85% 30%, ${platformConfig.accentColor}15, transparent 50%)`
      }} />

      <div className={styles.card}>
        {/* Header */}
        <div className={styles.cardHeader}>
          {onBack && (
            <button className={styles.backBtn} onClick={onBack}>
              <ArrowLeft size={16} /> Back
            </button>
          )}
          <div className={styles.platformBadge} style={{ background: platformConfig.gradient }}>
            <span>{platformConfig.name}</span>
            <span className={styles.formatDot}>·</span>
            <span>{format.label}</span>
          </div>
          <button className={styles.skipBtn} onClick={onSkip}>
            Skip, I'll create manually →
          </button>
        </div>

        {/* ─── STEP 1: Initial Prompt ─── */}
        {flowStep === 'prompt' && (
          <div className={styles.promptStep}>
            <div className={styles.aiIcon}>
              <Wand2 size={28} className={styles.aiIconSvg} />
            </div>
            <h2 className={styles.stepTitle}>What do you want to create?</h2>
            <p className={styles.stepSub}>
              Describe your idea in one or two sentences. Be as specific as you can — the more detail you give, the better the AI will understand.
            </p>

            <div className={styles.promptExamples}>
              {[
                `A ${format.label.toLowerCase()} about how to grow from 0 to 10K followers on ${platformConfig.name}`,
                `Behind-the-scenes of my morning routine as a content creator`,
                `5 mistakes people make when starting a business`,
              ].map((ex, i) => (
                <button 
                  key={ex} 
                  className={styles.examplePill} 
                  style={{ animationDelay: `${i * 0.05}s` }}
                  onClick={() => setConcept(ex)}
                >
                  {ex}
                </button>
              ))}
            </div>

            <div className={styles.inputWrapper}>
              <textarea
                ref={inputRef}
                className={styles.bigInput}
                placeholder={`e.g., A ${format.label.toLowerCase()} about how to grow your ${platformConfig.name} account from 0 to 10,000 followers using proven strategies…`}
                value={concept}
                onChange={e => setConcept(e.target.value)}
                rows={4}
                onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleConceptSubmit(); }}
              />
              
              <div className={styles.essentialsToolbar}>
                <button className={styles.essentialBtn} onClick={() => fileInputRef.current?.click()}>
                  <ImagePlus size={14} /> Add Media
                </button>
                <input type="file" multiple accept="image/*,video/*" hidden ref={fileInputRef} onChange={handleFileChange} />
                
                <button className={`${styles.essentialBtn} ${showLinkInput ? styles.essentialBtnActive : ''}`} onClick={() => setShowLinkInput(!showLinkInput)}>
                  <Link size={14} /> Add Link
                </button>
                
                <button className={`${styles.essentialBtn} ${showLocationInput ? styles.essentialBtnActive : ''}`} onClick={() => setShowLocationInput(!showLocationInput)}>
                  <MapPin size={14} /> Add Location
                </button>
              </div>

              {mediaFiles.length > 0 && (
                <div className={styles.mediaPreviewList}>
                  {mediaFiles.map((file, i) => (
                    <div key={i} className={styles.mediaPreviewItem}>
                      <span className={styles.mediaPreviewName}>{file.name}</span>
                      <button className={styles.mediaPreviewRemove} onClick={() => removeFile(i)}><X size={12} /></button>
                    </div>
                  ))}
                </div>
              )}

              {showLinkInput && (
                <div className={styles.essentialInputRow}>
                  <Link size={14} className={styles.essentialInputIcon} />
                  <input className={styles.essentialInput} placeholder="https://..." value={postLink} onChange={e => setPostLink(e.target.value)} />
                </div>
              )}

              {showLocationInput && (
                <div className={styles.essentialInputRow}>
                  <MapPin size={14} className={styles.essentialInputIcon} />
                  <input className={styles.essentialInput} placeholder="e.g., New York, NY" value={postLocation} onChange={e => setPostLocation(e.target.value)} />
                </div>
              )}

              <div className={styles.inputHint}>Press <kbd>Ctrl+Enter</kbd> to continue</div>
            </div>

            <button
              className={styles.primaryBtn}
              style={{ '--accent': platformConfig.accentColor, background: platformConfig.gradient } as any}
              onClick={handleConceptSubmit}
              disabled={!concept.trim()}
            >
              <Sparkles size={16} />
              Analyse & Start Creating
              <ArrowRight size={16} />
            </button>
          </div>
        )}

        {/* ─── STEP 2: 5 Questions ─── */}
        {flowStep === 'questions' && (
          <div className={styles.questionsStep}>
            {/* Progress */}
            <div className={styles.progressBar}>
              {questions.map((_, i) => (
                <div
                  key={i}
                  className={`${styles.progressDot} ${i < currentQ ? styles.progressDotDone : ''} ${i === currentQ ? styles.progressDotActive : ''}`}
                  style={i === currentQ ? { background: platformConfig.accentColor } : {}}
                />
              ))}
            </div>
            <div className={styles.progressLabel}>Question {currentQ + 1} of {questions.length}</div>

            {/* Concept recap */}
            <div className={styles.conceptRecap}>
              <span className={styles.conceptLabel}>Your idea:</span>
              <span className={styles.conceptText}>"{concept}"</span>
            </div>

            {/* Question */}
            <div className={styles.questionCard}>
              <div className={styles.questionNumber}>Q{currentQ + 1}</div>
              <h3 className={styles.questionText}>{questions[currentQ].question}</h3>
              <p className={styles.questionHint}>{questions[currentQ].hint}</p>
            </div>

            {/* Quick options if available */}
            {questions[currentQ].options && (
              <div className={styles.quickOptions}>
                {questions[currentQ].options!.map(opt => (
                  <button
                    key={opt}
                    className={`${styles.optionPill} ${currentAnswer === opt ? styles.optionPillActive : ''}`}
                    style={currentAnswer === opt ? { borderColor: platformConfig.accentColor, color: platformConfig.accentColor } : {}}
                    onClick={() => setCurrentAnswer(opt)}
                  >
                    {currentAnswer === opt && <Check size={12} />}
                    {opt}
                  </button>
                ))}
              </div>
            )}

            {/* Free text answer */}
            <textarea
              ref={inputRef}
              className={styles.answerInput}
              placeholder={questions[currentQ].placeholder}
              value={currentAnswer}
              onChange={e => setCurrentAnswer(e.target.value)}
              rows={3}
              onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleAnswerSubmit(); }}
            />
            <div className={styles.inputHint}>Press <kbd>Ctrl+Enter</kbd> to continue</div>

            <div className={styles.questionActions}>
              <button className={styles.skipAnswerBtn} onClick={handleAnswerSubmit}>
                Skip this question
              </button>
              <button
                className={styles.primaryBtn}
                style={{ background: platformConfig.gradient } as any}
                onClick={handleAnswerSubmit}
              >
                {currentQ < questions.length - 1 ? (
                  <>Next <ChevronRight size={16} /></>
                ) : (
                  <><Sparkles size={16} /> Start Generating!</>
                )}
              </button>
            </div>
          </div>
        )}

        {/* ─── STEP 3: Generation ─── */}
        {flowStep === 'generating' && (
          <div className={styles.generatingStep}>
            <div className={styles.generatingRing} style={{ '--accent': platformConfig.accentColor } as any}>
              <Sparkles size={32} className={styles.generatingIcon} />
            </div>
            <h2 className={styles.stepTitle}>Creating your {format.label}…</h2>
            <p className={styles.stepSub}>Hang tight — our AI is crafting content tailored specifically for {platformConfig.name}.</p>

            <div className={styles.genSteps}>
              {generationSteps.map((step, i) => (
                <div
                  key={i}
                  className={`${styles.genStep} ${i < generationStep ? styles.genStepDone : ''} ${i === generationStep - 1 && generationStep < generationSteps.length ? styles.genStepActive : ''}`}
                >
                  <div className={styles.genStepIcon}>
                    {i < generationStep ? <Check size={14} /> : i === generationStep - 1 ? <Loader2 size={14} className={styles.spin} /> : <span>{step.icon}</span>}
                  </div>
                  <span className={styles.genStepLabel}>{step.label}</span>
                </div>
              ))}
            </div>

            <div className={styles.genProgress}>
              <div
                className={styles.genProgressFill}
                style={{ width: `${(generationStep / generationSteps.length) * 100}%`, background: platformConfig.accentColor }}
              />
            </div>
          </div>
        )}

        {/* ─── STEP 4: Result ─── */}
        {flowStep === 'result' && result && (
          <div className={styles.resultStep}>
            <div className={styles.resultHeader}>
              <div className={styles.resultCheck} style={{ background: platformConfig.accentColor + '22', borderColor: platformConfig.accentColor + '44' }}>
                <Check size={20} style={{ color: platformConfig.accentColor }} />
              </div>
              <div>
                <h2 className={styles.resultTitle}>Your content is ready!</h2>
                <p className={styles.resultSub}>Review below, then choose how you want to proceed.</p>
              </div>
            </div>

            {/* Preview of generated content */}
            <div className={styles.resultPreview}>
              <div className={styles.previewSection}>
                <div className={styles.previewLabel}>Generated Caption</div>
                <div className={styles.previewContent}>{result.caption}</div>
              </div>
              {result.hashtags.length > 0 && (
                <div className={styles.previewSection}>
                  <div className={styles.previewLabel}>Hashtags</div>
                  <div className={styles.hashtagsRow}>
                    {result.hashtags.map(h => (
                      <span key={h} className={styles.hashTag} style={{ color: platformConfig.accentColor, borderColor: platformConfig.accentColor + '40' }}>{h}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* AI Edit option */}
            <div className={styles.editSection}>
              <div className={styles.editSectionTitle}>
                <MessageSquarePlus size={15} />
                Ask AI to refine something
              </div>
              <div className={styles.editRow}>
                <input
                  className={styles.editInput}
                  placeholder='e.g., "Make the hook more shocking" or "Add more emojis"'
                  value={editPrompt}
                  onChange={e => setEditPrompt(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter') handleEditWithPrompt(); }}
                  disabled={isEditing}
                />
                <button className={styles.editBtn} onClick={handleEditWithPrompt} disabled={isEditing || !editPrompt.trim()}>
                  {isEditing ? <Loader2 size={14} className={styles.spin} /> : <Sparkles size={14} />}
                </button>
              </div>
              {/* Quick edit suggestions */}
              <div className={styles.editSuggestions}>
                {['Make it shorter', 'Add more energy', 'Make it funnier', 'More professional', 'Add a statistic'].map(s => (
                  <button key={s} className={styles.editSuggestionPill} onClick={() => setEditPrompt(s)}>{s}</button>
                ))}
              </div>
            </div>

            {/* Final Actions */}
            <div className={styles.resultActions}>
              <button className={styles.resetBtn} onClick={handleReset}>
                <RotateCcw size={14} />
                Start over
              </button>
              <button className={styles.manualBtn} onClick={handleManualEdit}>
                <Pencil size={14} />
                Edit manually in studio
              </button>
              <button
                className={styles.acceptBtn}
                style={{ background: platformConfig.gradient } as any}
                onClick={handleAccept}
              >
                <Check size={15} />
                Accept & open studio
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Helper: generate relevant hashtags
function generateHashtags(platform: string, concept: string, tone: string): string[] {
  const words = concept.toLowerCase().split(' ').filter(w => w.length > 3).slice(0, 4);
  const base = words.map(w => '#' + w.replace(/[^a-z0-9]/g, ''));
  const toneMap: Record<string, string[]> = {
    'Inspirational': ['#motivation', '#mindset', '#growth'],
    'Educational': ['#learnontiktok', '#didyouknow', '#tips'],
    'Entertaining': ['#viral', '#trending', '#fyp'],
    'Professional': ['#business', '#entrepreneur', '#leadership'],
  };
  const platformTags: Record<string, string[]> = {
    'Instagram': ['#instagram', '#reels', '#instagood'],
    'TikTok': ['#fyp', '#foryoupage', '#tiktok'],
    'LinkedIn': ['#linkedin', '#professional', '#career'],
    'YouTube': ['#youtube', '#youtuber', '#subscribe'],
  };
  const extra = (toneMap[tone] || ['#content', '#creator', '#socialmedia']).slice(0, 3);
  const platTags = (platformTags[platform] || ['#socialmedia']).slice(0, 2);
  return [...base, ...extra, ...platTags].slice(0, 15);
}
