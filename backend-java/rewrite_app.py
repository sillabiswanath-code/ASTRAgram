import re

with open('../frontend-pure/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the new SegmentViewer component
NEW_SEGMENT_VIEWER = """function SegmentViewer({ segment, courseIndex, setCurrentView, setCourses }) {
    const [activeTab, setActiveTab] = useState('video');
    const [unlockedTabs, setUnlockedTabs] = useState({ video: true, read: false, quiz: false });
    const [isBuffering, setIsBuffering] = useState(false);
    const [bufferMsg, setBufferMsg] = useState('');
    const videoRef = React.useRef(null);

    // ── Quiz state ─────────────────────────────────────────────────────────
    const [quizIndex, setQuizIndex]       = useState(0);
    const [answers, setAnswers]           = useState({});   // { qIndex: userSelection }
    const [showResult, setShowResult]     = useState(false);
    const [quizComplete, setQuizComplete] = useState(false);
    const [draggedItem, setDraggedItem]   = useState(null); // For matching questions

    const questions = React.useMemo(() => {
        const q = segment.quiz;
        if (!q) return [];
        if (Array.isArray(q.questions) && q.questions.length > 0) return q.questions;
        if (q.question && q.options && q.answer) {
            return [{ type: 'single_mcq', question: q.question, options: q.options, answer: q.answer, difficulty: 'medium' }];
        }
        return [];
    }, [segment.quiz]);

    const currentQ  = questions[quizIndex] || {};
    const qType = currentQ.type || 'single_mcq';
    const totalQ    = questions.length;
    
    // Default selection structure based on type
    let defaultSelected = null;
    if (qType === 'multiple_mcq') defaultSelected = [];
    if (qType === 'match_following') defaultSelected = {};
    
    const selected  = answers[quizIndex] || defaultSelected;

    // Calculate if correct
    let isCorrect = false;
    if (showResult && currentQ) {
        if (qType === 'single_mcq') {
            isCorrect = selected === currentQ.answer;
        } else if (qType === 'multiple_mcq') {
            isCorrect = selected.length === currentQ.answer.length && 
                        selected.every(s => currentQ.answer.includes(s));
        } else if (qType === 'match_following') {
            isCorrect = currentQ.pairs.every(p => selected[p.left] === p.right);
        }
    }

    const difficultyConfig = {
        easy:   { label: 'EASY',   color: '#16a34a', bg: '#dcfce7' },
        medium: { label: 'MEDIUM', color: '#d97706', bg: '#fef9c3' },
        hard:   { label: 'HARD',   color: '#dc2626', bg: '#fee2e2' },
    };

    const handleVideoEnd = () => {
        setUnlockedTabs(prev => ({ ...prev, quiz: true }));
        setActiveTab('quiz');
    };

    // --- single_mcq handler ---
    const handleOptionSelect = (opt) => {
        if (showResult) return;
        setAnswers(prev => ({ ...prev, [quizIndex]: opt }));
        setShowResult(true);
    };

    // --- multiple_mcq handlers ---
    const toggleMultipleOption = (opt) => {
        if (showResult) return;
        setAnswers(prev => {
            const currentSelected = prev[quizIndex] || [];
            if (currentSelected.includes(opt)) {
                return { ...prev, [quizIndex]: currentSelected.filter(o => o !== opt) };
            } else {
                return { ...prev, [quizIndex]: [...currentSelected, opt] };
            }
        });
    };

    const checkMultipleAnswer = () => {
        if (!selected || selected.length === 0) return;
        const requiredAnswers = currentQ.answer.length;
        if (selected.length < requiredAnswers) {
            alert(`There is one more correct answer... Please select ${requiredAnswers} answers before checking. You have selected ${selected.length}.`);
            return;
        }
        setShowResult(true);
    };

    // --- match_following handlers ---
    const handleDragStart = (e, rightItem) => {
        if (showResult) {
            e.preventDefault();
            return;
        }
        setDraggedItem(rightItem);
        // Required for Firefox
        e.dataTransfer.setData('text/plain', rightItem);
    };

    const handleDrop = (e, leftKey) => {
        e.preventDefault();
        if (showResult || !draggedItem) return;
        setAnswers(prev => {
            const currentMapping = prev[quizIndex] || {};
            // Remove dragged item from any previous drops to allow swapping
            const newMapping = {};
            for (const [k, v] of Object.entries(currentMapping)) {
                if (v !== draggedItem) newMapping[k] = v;
            }
            newMapping[leftKey] = draggedItem;
            return { ...prev, [quizIndex]: newMapping };
        });
        setDraggedItem(null);
    };
    
    const removeMatch = (leftKey) => {
        if (showResult) return;
        setAnswers(prev => {
            const currentMapping = { ...(prev[quizIndex] || {}) };
            delete currentMapping[leftKey];
            return { ...prev, [quizIndex]: currentMapping };
        });
    };

    const checkMatchAnswer = () => {
        const requiredMatches = currentQ.pairs.length;
        const currentMatches = Object.keys(selected || {}).length;
        if (currentMatches < requiredMatches) {
            alert(`Please match all ${requiredMatches} pairs before checking.`);
            return;
        }
        setShowResult(true);
    };

    // --- General flow ---
    const handleNext = () => {
        setShowResult(false);
        if (quizIndex < totalQ - 1) {
            setQuizIndex(qi => qi + 1);
        } else {
            setQuizComplete(true);
        }
    };

    const handleRetryQuiz = () => {
        setQuizIndex(0);
        setAnswers({});
        setShowResult(false);
        setQuizComplete(false);
    };

    const handleNextSegment = () => {
        setCourses(prev => {
            const newCourses = [...prev];
            const course = { ...newCourses[courseIndex] };
            const newSegments = [...course.segments];
            const currentIdx = newSegments.findIndex(s => s.id === segment.id);
            if (currentIdx !== -1 && currentIdx + 1 < newSegments.length) {
                newSegments[currentIdx + 1] = { ...newSegments[currentIdx + 1], status: 'unlocked' };
            }
            course.segments = newSegments;
            newCourses[courseIndex] = course;
            return newCourses;
        });
        setCurrentView('course-map');
    };

    // Score calculation
    let finalScore = 0;
    questions.forEach((q, i) => {
        const sel = answers[i];
        if (!sel) return;
        if (q.type === 'single_mcq' || !q.type) {
            if (sel === q.answer) finalScore++;
        } else if (q.type === 'multiple_mcq') {
            if (sel.length === q.answer.length && sel.every(s => q.answer.includes(s))) finalScore++;
        } else if (q.type === 'match_following') {
            if (q.pairs.every(p => sel[p.left] === p.right)) finalScore++;
        }
    });
    
    const passMark = Math.ceil(totalQ * 0.6);

    return (
        <div className="page-container">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <button className="btn btn-secondary" onClick={() => setCurrentView('course-map')}>
                    <i className="fa-solid fa-arrow-left" style={{ marginRight: '8px' }}></i> Back to Course Map
                </button>
                <h1 className="page-title" style={{ marginBottom: 0 }}>{segment.title}</h1>
            </div>

            <div className="card">
                <div className="tabs">
                    <button className={`tab-btn ${activeTab === 'video' ? 'active' : ''}`} onClick={() => setActiveTab('video')}>
                        <i className="fa-solid fa-play" style={{ marginRight: '8px' }}></i> Watch Video
                    </button>
                    <button className={`tab-btn ${activeTab === 'quiz' ? 'active' : ''}`}
                        onClick={() => unlockedTabs.quiz && setActiveTab('quiz')}
                        disabled={!unlockedTabs.quiz}>
                        {unlockedTabs.quiz
                            ? <i className="fa-solid fa-clipboard-question" style={{ marginRight: '8px' }}></i>
                            : <i className="fa-solid fa-lock" style={{ marginRight: '8px' }}></i>}
                        Quiz {totalQ > 0 && `(${totalQ} Questions)`}
                    </button>
                </div>

                <div style={{ marginTop: '2rem' }}>
                    {activeTab === 'video' && (
                        <div>
                            <div className="video-container" style={{ position: 'relative' }}>
                                {isBuffering && (
                                    <div style={{ position: 'absolute', inset: 0, background: 'rgba(15,20,30,0.80)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', zIndex: 10, borderRadius: '10px', gap: '14px' }}>
                                        <i className="fa-solid fa-circle-notch fa-spin" style={{ fontSize: '2.5rem', color: 'var(--primary)' }}></i>
                                        <p style={{ color: '#fff', fontWeight: 600, fontSize: '0.95rem', textAlign: 'center', padding: '0 1.5rem' }}>{bufferMsg}</p>
                                    </div>
                                )}
                                <video ref={videoRef} className="video-player" controls preload="auto" src={segment.video_url}
                                    onWaiting={() => { setIsBuffering(true); setBufferMsg('Buffering...'); }}
                                    onPlaying={() => setIsBuffering(false)}
                                    onEnded={handleVideoEnd}
                                    style={{ display: 'block', width: '100%' }}>
                                    Your browser does not support the video tag.
                                </video>
                            </div>
                            {!unlockedTabs.quiz && (
                                <p style={{ textAlign: 'center', marginTop: '1rem', color: 'var(--text-muted)' }}>
                                    Finish watching to unlock the Quiz 🔒
                                </p>
                            )}
                        </div>
                    )}

                    {activeTab === 'quiz' && (
                        <div>
                            {totalQ === 0 ? (
                                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                                    No quiz available for this segment.
                                </div>
                            ) : quizComplete ? (
                                <div style={{ textAlign: 'center', padding: '2rem', backgroundColor: '#f8fafc', borderRadius: '0.5rem' }}>
                                    <h2 style={{ fontSize: '2rem', marginBottom: '1rem' }}>Quiz Complete!</h2>
                                    <p style={{ fontSize: '1.2rem', marginBottom: '2rem' }}>
                                        You scored {finalScore} out of {totalQ}
                                    </p>
                                    {finalScore >= passMark ? (
                                        <div>
                                            <p style={{ color: '#047857', marginBottom: '1rem' }}><i className="fa-solid fa-circle-check"></i> Great job! You passed.</p>
                                            <button className="btn btn-primary" onClick={handleNextSegment}>Continue to Next Segment</button>
                                        </div>
                                    ) : (
                                        <div>
                                            <p style={{ color: '#b91c1c', marginBottom: '1rem' }}><i className="fa-solid fa-circle-xmark"></i> You didn't quite pass. Try again!</p>
                                            <button className="btn btn-secondary" onClick={handleRetryQuiz}>Retry Quiz</button>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                                        <span style={{ fontWeight: 'bold' }}>Question {quizIndex + 1} of {totalQ}</span>
                                        {currentQ?.difficulty && (
                                            <span style={{ 
                                                fontSize: '0.8rem', padding: '0.2rem 0.6rem', borderRadius: '1rem', 
                                                backgroundColor: difficultyConfig[currentQ.difficulty]?.bg || '#f1f5f9',
                                                color: difficultyConfig[currentQ.difficulty]?.color || '#475569',
                                                fontWeight: 'bold' 
                                            }}>
                                                {difficultyConfig[currentQ.difficulty]?.label || currentQ.difficulty.toUpperCase()}
                                            </span>
                                        )}
                                    </div>
                                    <h2 style={{ fontSize: '1.5rem', marginBottom: '2rem' }}>{currentQ?.question}</h2>
                                    
                                    {/* --- SINGLE MCQ --- */}
                                    {(qType === 'single_mcq' || !qType) && (
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                            {currentQ?.options?.map((opt, i) => {
                                                let btnClass = 'btn-secondary';
                                                if (showResult) {
                                                    if (opt === currentQ.answer) {
                                                        btnClass = 'btn-primary';
                                                    } else if (opt === selected) {
                                                        btnClass = 'btn-danger';
                                                    }
                                                }
                                                return (
                                                    <button key={i} className={`btn ${btnClass}`}
                                                        style={{ 
                                                            justifyContent: 'flex-start', padding: '1rem',
                                                            backgroundColor: btnClass === 'btn-danger' ? '#fee2e2' : undefined,
                                                            color: btnClass === 'btn-danger' ? '#b91c1c' : undefined,
                                                            borderColor: btnClass === 'btn-danger' ? '#f87171' : undefined
                                                        }}
                                                        onClick={() => handleOptionSelect(opt)} disabled={showResult}>
                                                        <div style={{ width: '30px', height: '30px', borderRadius: '50%', border: '1px solid currentColor', display: 'flex', alignItems: 'center', justifyContent: 'center', marginRight: '1rem' }}>
                                                            {String.fromCharCode(65 + i)}
                                                        </div>
                                                        {opt}
                                                    </button>
                                                );
                                            })}
                                        </div>
                                    )}

                                    {/* --- MULTIPLE MCQ --- */}
                                    {qType === 'multiple_mcq' && (
                                        <div>
                                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
                                                {currentQ?.options?.map((opt, i) => {
                                                    const isChecked = selected && selected.includes(opt);
                                                    let bgClass = isChecked ? '#e0f2fe' : '#ffffff';
                                                    let borderClass = isChecked ? '#0ea5e9' : '#e2e8f0';
                                                    let textClass = '#1e293b';
                                                    
                                                    if (showResult) {
                                                        const isCorrectOpt = currentQ.answer.includes(opt);
                                                        if (isCorrectOpt) {
                                                            bgClass = '#dcfce7'; borderClass = '#22c55e'; textClass = '#16a34a';
                                                        } else if (isChecked && !isCorrectOpt) {
                                                            bgClass = '#fee2e2'; borderClass = '#ef4444'; textClass = '#dc2626';
                                                        }
                                                    }

                                                    return (
                                                        <div key={i} 
                                                            style={{ 
                                                                display: 'flex', alignItems: 'center', padding: '1rem', 
                                                                borderRadius: '0.5rem', border: `2px solid ${borderClass}`, 
                                                                backgroundColor: bgClass, color: textClass,
                                                                cursor: showResult ? 'default' : 'pointer',
                                                                transition: 'all 0.2s'
                                                            }}
                                                            onClick={() => toggleMultipleOption(opt)}
                                                        >
                                                            <div style={{ 
                                                                width: '24px', height: '24px', borderRadius: '4px', 
                                                                border: `2px solid ${borderClass}`, marginRight: '1rem',
                                                                backgroundColor: isChecked ? borderClass : 'transparent',
                                                                display: 'flex', alignItems: 'center', justifyContent: 'center'
                                                            }}>
                                                                {isChecked && <i className="fa-solid fa-check" style={{ color: 'white', fontSize: '12px' }}></i>}
                                                            </div>
                                                            {opt}
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                            {!showResult && (
                                                <button className="btn btn-primary" onClick={checkMultipleAnswer}>
                                                    Check Answer
                                                </button>
                                            )}
                                        </div>
                                    )}

                                    {/* --- MATCH THE FOLLOWING --- */}
                                    {qType === 'match_following' && (
                                        <div>
                                            <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
                                                Drag the options from the right pool and drop them onto the matching slots on the left.
                                            </p>
                                            <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
                                                {/* Left Targets */}
                                                <div style={{ flex: '1 1 300px', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                                    {currentQ.pairs.map((p, i) => {
                                                        const matchedItem = selected[p.left];
                                                        let borderClass = '#cbd5e1';
                                                        let bgClass = '#f8fafc';
                                                        if (showResult) {
                                                            const isCorrectMatch = matchedItem === p.right;
                                                            if (isCorrectMatch) {
                                                                borderClass = '#22c55e'; bgClass = '#dcfce7';
                                                            } else {
                                                                borderClass = '#ef4444'; bgClass = '#fee2e2';
                                                            }
                                                        } else if (matchedItem) {
                                                            borderClass = '#0ea5e9'; bgClass = '#e0f2fe';
                                                        }

                                                        return (
                                                            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                                                <div style={{ flex: 1, padding: '1rem', backgroundColor: '#f1f5f9', borderRadius: '0.5rem', fontWeight: 500 }}>
                                                                    {p.left}
                                                                </div>
                                                                <div style={{ color: '#94a3b8' }}><i className="fa-solid fa-arrow-right"></i></div>
                                                                <div 
                                                                    onDragOver={(e) => e.preventDefault()}
                                                                    onDrop={(e) => handleDrop(e, p.left)}
                                                                    style={{ 
                                                                        flex: 1, padding: matchedItem ? '0.8rem' : '1rem', 
                                                                        border: `2px dashed ${borderClass}`, 
                                                                        backgroundColor: bgClass,
                                                                        borderRadius: '0.5rem', minHeight: '60px',
                                                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                                        position: 'relative'
                                                                    }}
                                                                >
                                                                    {matchedItem ? (
                                                                        <div style={{ 
                                                                            backgroundColor: 'white', padding: '0.6rem 1rem', 
                                                                            borderRadius: '0.3rem', boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                                                                            width: '100%', textAlign: 'center', position: 'relative'
                                                                        }}>
                                                                            {matchedItem}
                                                                            {!showResult && (
                                                                                <button onClick={() => removeMatch(p.left)} style={{ position: 'absolute', top: '-8px', right: '-8px', background: '#ef4444', color: 'white', border: 'none', borderRadius: '50%', width: '20px', height: '20px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '10px' }}>
                                                                                    <i className="fa-solid fa-xmark"></i>
                                                                                </button>
                                                                            )}
                                                                        </div>
                                                                    ) : (
                                                                        <span style={{ color: '#cbd5e1', fontSize: '0.9rem' }}>Drop here</span>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        );
                                                    })}
                                                </div>

                                                {/* Right Source Pool */}
                                                <div style={{ flex: '1 1 200px', backgroundColor: '#f8fafc', padding: '1.5rem', borderRadius: '0.5rem', border: '1px solid #e2e8f0' }}>
                                                    <h4 style={{ marginBottom: '1rem', color: '#64748b' }}>Options Pool</h4>
                                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
                                                        {currentQ.pairs
                                                            .map(p => p.right)
                                                            // We should shuffle these, but for simplicity we rely on React rendering them. We can sort alphabetically to mix them up.
                                                            .sort((a, b) => a.localeCompare(b))
                                                            .map((rightItem, i) => {
                                                                // Hide if already used
                                                                const isUsed = Object.values(selected || {}).includes(rightItem);
                                                                if (isUsed) return null;
                                                                
                                                                return (
                                                                    <div 
                                                                        key={i}
                                                                        draggable={!showResult}
                                                                        onDragStart={(e) => handleDragStart(e, rightItem)}
                                                                        style={{ 
                                                                            backgroundColor: 'white', padding: '0.8rem', 
                                                                            borderRadius: '0.5rem', border: '1px solid #cbd5e1',
                                                                            cursor: showResult ? 'default' : 'grab',
                                                                            boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                                                                            opacity: draggedItem === rightItem ? 0.5 : 1
                                                                        }}
                                                                    >
                                                                        {rightItem}
                                                                    </div>
                                                                );
                                                            })
                                                        }
                                                    </div>
                                                </div>
                                            </div>
                                            {!showResult && (
                                                <button className="btn btn-primary" onClick={checkMatchAnswer} style={{ marginTop: '1.5rem' }}>
                                                    Check Answer
                                                </button>
                                            )}
                                        </div>
                                    )}

                                    {/* --- SHARED RESULT AREA --- */}
                                    {showResult && (
                                        <div style={{ marginTop: '2rem', padding: '1.5rem', backgroundColor: isCorrect ? '#ecfdf5' : '#fee2e2', color: isCorrect ? '#047857' : '#b91c1c', borderRadius: '0.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <div>
                                                <h3 style={{ margin: 0, display: 'flex', alignItems: 'center' }}>
                                                    {isCorrect 
                                                        ? <><i className="fa-solid fa-circle-check" style={{ marginRight: '0.5rem' }}></i> Correct!</>
                                                        : <><i className="fa-solid fa-circle-xmark" style={{ marginRight: '0.5rem' }}></i> Incorrect</>
                                                    }
                                                </h3>
                                                
                                                {!isCorrect && qType === 'single_mcq' && <p style={{ marginTop: '0.5rem', marginBottom: 0 }}>The correct answer is: <strong>{currentQ.answer}</strong></p>}
                                                {!isCorrect && qType === 'multiple_mcq' && <p style={{ marginTop: '0.5rem', marginBottom: 0 }}>The correct answers were: <strong>{currentQ.answer.join(' & ')}</strong></p>}
                                                {!isCorrect && qType === 'match_following' && <p style={{ marginTop: '0.5rem', marginBottom: 0 }}>Check the matching logic carefully.</p>}
                                                
                                                {currentQ?.explanation && <p style={{ marginTop: '0.5rem', marginBottom: 0, fontStyle: 'italic' }}>{currentQ.explanation}</p>}
                                            </div>
                                            <button className="btn" style={{ backgroundColor: isCorrect ? '#047857' : '#b91c1c', color: 'white' }} onClick={handleNext}>
                                                {quizIndex < totalQ - 1 ? 'Next Question' : 'View Results'}
                                            </button>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}"""

# Use regex to find and replace the entire function SegmentViewer
pattern = re.compile(r'function SegmentViewer\(\{\s*segment,\s*courseIndex,\s*setCurrentView,\s*setCourses\s*\}\)\s*\{[\s\S]*?\}\s*function CodeGraphAuth', re.MULTILINE)

new_content = pattern.sub(NEW_SEGMENT_VIEWER + '\n\nfunction CodeGraphAuth', content)

if new_content != content:
    with open('../frontend-pure/app.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully replaced SegmentViewer in app.js!")
else:
    print("Error: Could not find SegmentViewer to replace.")
