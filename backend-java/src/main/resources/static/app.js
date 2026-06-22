const { useState, useEffect } = React;

// --- Logo Components ---

// Static logo mark used everywhere after splash
function LogoMark({ size, variant }) {
    size = size || 'medium';
    variant = variant || 'dark';
    const fontSizes = { small: '1.15rem', medium: '1.8rem', large: '2.6rem' };
    const dotSizes  = { small: '7px',     medium: '10px',   large: '14px' };
    const mbDot     = { small: '1px',     medium: '3px',    large: '5px' };
    const textColor = variant === 'light' ? '#f1f5f9' : '#1c2230';
    return (
        <span style={{ display: 'inline-flex', alignItems: 'flex-end', gap: '3px', lineHeight: 1 }}>
            <span style={{
                fontFamily: "'Inter', 'Segoe UI', sans-serif",
                fontWeight: 800,
                fontSize: fontSizes[size],
                color: textColor,
                letterSpacing: '-0.5px'
            }}>astragram</span>
            <span style={{
                width: dotSizes[size],
                height: dotSizes[size],
                borderRadius: '50%',
                background: '#f57c00',
                display: 'inline-block',
                flexShrink: 0,
                marginBottom: mbDot[size]
            }} />
        </span>
    );
}

// Full-screen splash shown once on first page load
function LogoSplash({ onDone }) {
    useEffect(() => {
        // Match CSS animation total: 2.4s delay + 0.6s fade = 3.0s
        const t = setTimeout(onDone, 3100);
        return () => clearTimeout(t);
    }, []);
    return (
        <div className="logo-scene">
            <div className="bg-reveal" />
            <div className="logo-wrapper">
                <div className="logo-pill" />
                <div className="text-mask">
                    <h1 className="logo-text-anim">astragram</h1>
                </div>
                <div className="logo-dot-anim" />
            </div>
        </div>
    );
}

// --- Components ---

function Navbar({ currentView, setCurrentView }) {
    return (
        <header className="navbar">
            <div className="nav-brand" style={{ cursor: 'pointer' }} onClick={() => setCurrentView('home')}>
                <LogoMark size="small" variant="dark" />
            </div>
            <nav className="nav-links">
                <a href="#" className="nav-link" onClick={() => setCurrentView('home')}>Home</a>
                <a href="#" className="nav-link" onClick={() => setCurrentView('my-courses')}>Courses</a>
                <a href="#" className="nav-link">Blog</a>
                <a href="#" className="nav-link">Contact</a>
            </nav>
            <button className="btn btn-primary" onClick={() => setCurrentView('builder')} style={{ cursor: 'pointer' }}>
                Build Course
            </button>
        </header>
    );
}

function Home({ setCurrentView }) {
    return (
        <div className="page-container">
            <div className="hero-section">
                <div className="hero-content">
                    <h1 className="page-title">
                        Learning is key to your<br/>success. Get custom<br/>designed courses
                    </h1>
                    <p style={{ fontSize: '1.1rem', color: 'var(--text-muted)', marginBottom: '2rem', maxWidth: '500px' }}>
                        Transform YouTube videos into interactive learning experiences in seconds.
                    </p>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <button className="btn btn-primary" onClick={() => setCurrentView('builder')} style={{ cursor: 'pointer' }}>
                            Get Started <i className="fa-solid fa-arrow-right" style={{ marginLeft: '8px' }}></i>
                        </button>
                        <button className="btn btn-secondary" onClick={() => setCurrentView('my-courses')} style={{ cursor: 'pointer' }}>
                            <i className="fa-solid fa-play" style={{ color: 'var(--primary)', marginRight: '8px' }}></i> How it works
                        </button>
                    </div>
                </div>
                <div style={{ flex: 1, textAlign: 'right' }}>
                    <img src="https://img.freepik.com/free-vector/telecommuting-concept-illustration_114360-1600.jpg" alt="Hero Illustration" style={{ width: '100%', maxWidth: '500px', borderRadius: '1rem' }} />
                </div>
            </div>

            <div style={{ marginTop: '4rem' }}>
                <h2 style={{ fontSize: '2rem', fontWeight: '800', marginBottom: '2rem' }}>Explore by<br/>categories</h2>
                <div className="course-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
                    <div className="card" style={{ textAlign: 'center', cursor: 'pointer', padding: '2rem' }}>
                        <div style={{ background: '#fffbeb', width: '60px', height: '60px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
                            <i className="fa-solid fa-lock" style={{ color: '#d97706', fontSize: '1.5rem' }}></i>
                        </div>
                        <h3 style={{ marginBottom: '0.5rem' }}>Powerful logic</h3>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>AI-driven content parsing</p>
                    </div>
                    <div className="card" style={{ textAlign: 'center', cursor: 'pointer', padding: '2rem' }}>
                        <div style={{ background: '#ffe4e6', width: '60px', height: '60px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
                            <i className="fa-solid fa-code" style={{ color: '#e11d48', fontSize: '1.5rem' }}></i>
                        </div>
                        <h3 style={{ marginBottom: '0.5rem' }}>Semantic structuring</h3>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Transcripts turned to chapters</p>
                    </div>
                    <div className="card" style={{ textAlign: 'center', cursor: 'pointer', padding: '2rem' }}>
                        <div style={{ background: '#dcfce7', width: '60px', height: '60px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
                            <i className="fa-solid fa-cubes" style={{ color: '#16a34a', fontSize: '1.5rem' }}></i>
                        </div>
                        <h3 style={{ marginBottom: '0.5rem' }}>Interactive Quizzes</h3>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Test your knowledge instantly</p>
                    </div>
                    <div className="card" style={{ textAlign: 'center', cursor: 'pointer', padding: '2rem' }}>
                        <div style={{ background: '#e0f2fe', width: '60px', height: '60px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
                            <i className="fa-solid fa-bolt" style={{ color: '#0284c7', fontSize: '1.5rem' }}></i>
                        </div>
                        <h3 style={{ marginBottom: '0.5rem' }}>Fast processing</h3>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Ready to learn in seconds</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

function CourseBuilder({ setCourses, setCurrentView, setCurrentCourseIndex }) {
    const [url, setUrl] = useState('');
    const [fastMode, setFastMode] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [loadingMessage, setLoadingMessage] = useState('Starting engine...');
    const [progress, setProgress] = useState(0);

    const handleBuild = (e) => {
        e.preventDefault();
        if (!url) return;
        
        setLoading(true);
        setError(null);
        setProgress(0);
        setLoadingMessage('Initializing...');
        
        const eventSource = new EventSource(`/api/course/stream-build?url=${encodeURIComponent(url)}&format=pdf&fastMode=${fastMode}`);
        
        eventSource.addEventListener('progress', (e) => {
            const data = e.data;
            const splitIdx = data.indexOf(':');
            if (splitIdx !== -1) {
                const pct = parseInt(data.substring(0, splitIdx), 10);
                const msg = data.substring(splitIdx + 1);
                setProgress(pct);
                setLoadingMessage(msg);
            }
        });
        
        eventSource.addEventListener('result', (e) => {
            const data = JSON.parse(e.data);
            if (data.error) {
                setError(data.error);
                setLoading(false);
            } else {
                setCourses(prev => {
                    const updated = [...prev, data];
                    setCurrentCourseIndex(updated.length - 1);
                    return updated;
                });
                setCurrentView('course-map');
                setLoading(false);
            }
            eventSource.close();
        });
        
        eventSource.onerror = (err) => {
            setError('Connection to server lost or failed.');
            eventSource.close();
            setLoading(false);
        };
    };

    return (
        <div className="page-container">
            <h1 className="page-title">Course Builder</h1>
            <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
                <p className="mb-4" style={{ color: 'var(--text-muted)' }}>
                    Paste a YouTube link below. We'll download it, analyze the transcript, cut it into 3-minute segments, and generate reading materials & quizzes.
                </p>
                <form onSubmit={handleBuild}>
                    <div className="form-group">
                        <label className="form-label">YouTube URL</label>
                        <input 
                            type="text" 
                            className="form-input" 
                            placeholder="https://www.youtube.com/watch?v=..."
                            value={url}
                            onChange={e => setUrl(e.target.value)}
                            disabled={loading}
                        />
                    </div>
                    <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <input 
                            type="checkbox" 
                            id="fastMode" 
                            checked={fastMode}
                            onChange={(e) => setFastMode(e.target.checked)}
                            disabled={loading}
                            style={{ width: '18px', height: '18px', accentColor: 'var(--primary)' }}
                        />
                        <label htmlFor="fastMode" style={{ margin: 0, cursor: 'pointer', color: 'var(--text-main)', fontWeight: '500' }}>
                            Fast Mode (Skip AI Evaluation)
                        </label>
                    </div>
                    {error && (
                        <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '1rem', borderRadius: '0.5rem', marginBottom: '1rem' }}>
                            <i className="fa-solid fa-circle-exclamation mr-2"></i> {error}
                        </div>
                    )}
                    
                    {loading ? (
                        <div style={{ padding: '2rem', backgroundColor: '#f8fafc', borderRadius: '0.5rem', border: '1px solid #e2e8f0' }}>
                            <h3 style={{ fontSize: '1.2rem', color: 'var(--text-main)', marginBottom: '1.5rem', textAlign: 'center' }}>Building your course...</h3>
                            
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem', fontSize: '0.95rem' }}>
                                <span style={{ color: 'var(--primary-dark)', fontWeight: 'bold' }}>
                                    <i className="fa-solid fa-circle-notch fa-spin" style={{ marginRight: '8px' }}></i>
                                    {loadingMessage}
                                </span>
                                <span style={{ fontWeight: 'bold', color: 'var(--text-main)' }}>{progress}%</span>
                            </div>
                            
                            <div style={{ width: '100%', height: '12px', backgroundColor: '#e2e8f0', borderRadius: '6px', overflow: 'hidden', marginBottom: '0.5rem' }}>
                                <div style={{ height: '100%', width: `${progress}%`, backgroundColor: 'var(--primary)', transition: 'width 0.3s ease-out' }}></div>
                            </div>
                        </div>
                    ) : (
                        <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
                            Generate ASTRAgram Course
                        </button>
                    )}
                </form>
            </div>
        </div>
    );
}

function MyCoursesDashboard({ courses, setCurrentView, setCurrentCourseIndex }) {
    if (!courses || courses.length === 0) {
        return (
            <div className="page-container text-center">
                <h1 className="page-title">Your Courses</h1>
                <p className="mb-4" style={{ color: 'var(--text-muted)' }}>You haven't built any courses yet.</p>
                <button className="btn btn-primary" onClick={() => setCurrentView('builder')}>Go to Course Builder</button>
            </div>
        );
    }

    return (
        <div className="page-container">
            <h1 className="page-title">Featured courses for you</h1>
            <div className="course-grid">
                {courses.map((course, idx) => {
                    const fallbackThumbnail = 'https://images.unsplash.com/photo-1497646654767-f2732049e6f1?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=60';
                    const thumbnailUrl = course.youtube_id 
                        ? `https://img.youtube.com/vi/${course.youtube_id}/mqdefault.jpg`
                        : fallbackThumbnail;
                        
                    return (
                        <div key={idx} className="card" style={{ cursor: 'pointer', overflow: 'hidden', padding: 0, transition: 'transform 0.2s', border: '1px solid #e2e8f0' }} onClick={() => {
                            setCurrentCourseIndex(idx);
                            setCurrentView('course-map');
                        }}
                        onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
                        onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                        >
                            <div style={{ height: '140px', overflow: 'hidden' }}>
                                <img src={thumbnailUrl} alt="Thumbnail" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                            </div>
                            <div style={{ padding: '1.2rem' }}>
                                <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                    {course.course_title || "Course"}
                                </h3>
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                                    <i className="fa-solid fa-layer-group" style={{ marginRight: '6px' }}></i>
                                    {course.segments ? course.segments.length : 0} Segments
                                </p>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

function CourseMap({ course, setCurrentView, setCurrentSegment }) {
    if (!course) return null;
    
    return (
        <div className="page-container">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <button className="btn btn-secondary" onClick={() => setCurrentView('my-courses')}>
                    <i className="fa-solid fa-arrow-left" style={{ marginRight: '8px' }}></i> Back to Dashboard
                </button>
            </div>
            
            <h1 className="page-title">{course.course_title || "Course Details"}</h1>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                {course.segments.map((seg, idx) => (
                    <div key={seg.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', opacity: seg.status === 'locked' ? 0.6 : 1 }}>
                        <div>
                            <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                                {seg.status === 'locked' ? <i className="fa-solid fa-lock" style={{ color: 'var(--text-muted)', marginRight: '8px' }}></i> : <i className="fa-solid fa-unlock" style={{ color: 'var(--primary)', marginRight: '8px' }}></i>}
                                {seg.title}
                            </h3>
                            <p style={{ color: 'var(--text-muted)' }}>Phase {idx + 1} - 3 Minute Video & Quiz</p>
                        </div>
                        {seg.status !== 'locked' && (
                            <button className="btn btn-primary" onClick={() => {
                                setCurrentSegment(seg);
                                setCurrentView('segment');
                            }}>
                                Start Segment <i className="fa-solid fa-arrow-right" style={{ marginLeft: '8px' }}></i>
                            </button>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}

function SegmentViewer({ segment, courseIndex, setCurrentView, setCourses }) {
    const [activeTab, setActiveTab] = useState('video');
    const [unlockedTabs, setUnlockedTabs] = useState({ video: true, read: false, quiz: false });
    const [quizAnswered, setQuizAnswered] = useState(false);
    const [selectedOption, setSelectedOption] = useState(null);
    const [attempts, setAttempts] = useState(0);
    const [isBuffering, setIsBuffering] = useState(false);
    const [bufferMsg, setBufferMsg] = useState('');
    const videoRef = React.useRef(null);

    // ── Quiz state ─────────────────────────────────────────────────────────
    const [quizIndex, setQuizIndex]       = useState(0);
    const [answers, setAnswers]           = useState({});   // { qIndex: selectedOption }
    const [showResult, setShowResult]     = useState(false);
    const [quizComplete, setQuizComplete] = useState(false);

    // Normalise quiz data: support both new {questions:[...]} and legacy {question,...}
    const questions = React.useMemo(() => {
        const q = segment.quiz;
        if (!q) return [];
        if (Array.isArray(q.questions) && q.questions.length > 0) return q.questions;
        if (q.question && q.options && q.answer) {
            return [{ question: q.question, options: q.options, answer: q.answer, difficulty: 'medium' }];
        }
        return [];
    }, [segment.quiz]);

    const currentQ  = questions[quizIndex];
    const totalQ    = questions.length;
    const selected  = answers[quizIndex];
    const isCorrect = selected === (currentQ && currentQ.answer);

    const difficultyConfig = {
        easy:   { label: 'EASY',   color: '#16a34a', bg: '#dcfce7' },
        medium: { label: 'MEDIUM', color: '#d97706', bg: '#fef9c3' },
        hard:   { label: 'HARD',   color: '#dc2626', bg: '#fee2e2' },
    };

    const handleVideoEnd = () => {
        setUnlockedTabs(prev => ({ ...prev, quiz: true }));
        setActiveTab('quiz');
    };

    const handleOptionSelect = (opt) => {
        if (selected) return;
        setAnswers(prev => ({ ...prev, [quizIndex]: opt }));
        setShowResult(true);
    };

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

    const finalScore = questions.filter((q, i) => answers[i] === q.answer).length;
    const passMark   = Math.ceil(totalQ * 0.6);

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

                    {/* ── VIDEO TAB ─────────────────────────────────────────────── */}
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

                    {/* ── QUIZ TAB ──────────────────────────────────────────────── */}
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
                                                <button 
                                                    key={i} 
                                                    className={`btn ${btnClass}`}
                                                    style={{ 
                                                        justifyContent: 'flex-start', 
                                                        padding: '1rem',
                                                        backgroundColor: btnClass === 'btn-danger' ? '#fee2e2' : undefined,
                                                        color: btnClass === 'btn-danger' ? '#b91c1c' : undefined,
                                                        borderColor: btnClass === 'btn-danger' ? '#f87171' : undefined
                                                    }}
                                                    onClick={() => handleOptionSelect(opt)}
                                                    disabled={showResult}
                                                >
                                                    <div style={{ width: '30px', height: '30px', borderRadius: '50%', border: '1px solid currentColor', display: 'flex', alignItems: 'center', justifyContent: 'center', marginRight: '1rem' }}>
                                                        {String.fromCharCode(65 + i)}
                                                    </div>
                                                    {opt}
                                                </button>
                                            );
                                        })}
                                    </div>
                                    
                                    {showResult && (
                                        <div style={{ marginTop: '2rem', padding: '1.5rem', backgroundColor: isCorrect ? '#ecfdf5' : '#fee2e2', color: isCorrect ? '#047857' : '#b91c1c', borderRadius: '0.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <div>
                                                <h3 style={{ margin: 0, display: 'flex', alignItems: 'center' }}>
                                                    {isCorrect 
                                                        ? <><i className="fa-solid fa-circle-check" style={{ marginRight: '0.5rem' }}></i> Correct!</>
                                                        : <><i className="fa-solid fa-circle-xmark" style={{ marginRight: '0.5rem' }}></i> Incorrect</>
                                                    }
                                                </h3>
                                                {!isCorrect && <p style={{ marginTop: '0.5rem', marginBottom: 0 }}>The correct answer is: <strong>{currentQ.answer}</strong></p>}
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
}

function CodeGraphAuth({ onUnlock }) {
    const [password, setPassword] = useState('');
    const [error, setError] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (password === '123456') {
            setError(false);
            onUnlock();
        } else {
            setError(true);
        }
    };

    return (
        <div className="page-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 'calc(100vh - 160px)' }}>
            <div className="card" style={{ maxWidth: '400px', width: '100%', textAlign: 'center', padding: '2.5rem 2rem', border: '1px solid #e2e8f0', borderRadius: '12px' }}>
                <div style={{ width: '60px', height: '60px', borderRadius: '50%', backgroundColor: '#fee2e2', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem auto' }}>
                    <i className="fa-solid fa-lock" style={{ fontSize: '1.5rem', color: '#ef4444' }}></i>
                </div>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Enter Password</h2>
                <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
                    Access to the Code Knowledge Graph is password protected.
                </p>
                <form onSubmit={handleSubmit}>
                    <div className="form-group" style={{ textAlign: 'left' }}>
                        <label className="form-label">Password</label>
                        <input 
                            type="password" 
                            className="form-input" 
                            placeholder="••••••" 
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required 
                            autoFocus
                        />
                    </div>
                    {error && (
                        <div style={{ color: '#ef4444', fontSize: '0.85rem', marginBottom: '1rem', textAlign: 'left' }}>
                            <i className="fa-solid fa-triangle-exclamation mr-1"></i> Incorrect password. Please try again.
                        </div>
                    )}
                    <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
                        Unlock Graph
                    </button>
                </form>
            </div>
        </div>
    );
}

function SignIn({ setIsAuthenticated }) {
    const handleLogin = (e) => {
        e.preventDefault();
        setIsAuthenticated(true);
    };

    return (
        <div className="auth-wrapper">
            <div className="glass-card">
                <div style={{ marginBottom: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <LogoMark size="large" variant="dark" />
                    <p style={{ color: 'var(--text-muted)', marginTop: '1rem' }}>Welcome back! Please sign in to continue.</p>
                </div>

                <button className="oauth-btn oauth-google" onClick={handleLogin}>
                    <i className="fa-brands fa-google" style={{ marginRight: '10px', fontSize: '1.2rem', color: '#DB4437' }}></i>
                    Continue with Google
                </button>
                <button className="oauth-btn oauth-github" onClick={handleLogin}>
                    <i className="fa-brands fa-github" style={{ marginRight: '10px', fontSize: '1.2rem' }}></i>
                    Continue with GitHub
                </button>

                <div className="auth-divider">
                    <span>OR</span>
                </div>

                <form onSubmit={handleLogin} style={{ textAlign: 'left' }}>
                    <div className="form-group">
                        <label className="form-label">Email Address</label>
                        <input type="email" className="form-input" placeholder="you@example.com" required />
                    </div>
                    <div className="form-group" style={{ marginBottom: '2rem' }}>
                        <label className="form-label">Password</label>
                        <input type="password" className="form-input" placeholder="••••••••" required />
                    </div>
                    <button type="submit" className="btn btn-primary" style={{ width: '100%', fontSize: '1.1rem', padding: '0.85rem' }}>
                        Sign In
                    </button>
                </form>
            </div>
        </div>
    );
}

// --- Main App Setup ---

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [currentView, setCurrentView] = useState('home');
    const [courses, setCourses] = useState([]);
    const [currentCourseIndex, setCurrentCourseIndex] = useState(null);
    const [currentSegment, setCurrentSegment] = useState(null);
    const [isGraphUnlocked, setIsGraphUnlocked] = useState(false);
    const [showSplash, setShowSplash] = useState(
        () => sessionStorage.getItem('splashPlayed') !== 'true'
    );

    if (showSplash) {
        return <LogoSplash onDone={() => {
            sessionStorage.setItem('splashPlayed', 'true');
            setShowSplash(false);
        }} />;
    }

    if (!isAuthenticated) {
        return <SignIn setIsAuthenticated={setIsAuthenticated} />;
    }

    const handleCodeGraphClick = () => {
        if (isGraphUnlocked) {
            setCurrentView('codegraph');
        } else {
            setCurrentView('codegraph-auth');
        }
    };

    return (
        <div className="app-container" style={{ flexDirection: 'column' }}>
            <Navbar currentView={currentView} setCurrentView={setCurrentView} />
            <main style={{ flex: 1 }}>
                
                {currentView === 'home' && <Home setCurrentView={setCurrentView} />}
                
                {currentView === 'builder' && <CourseBuilder setCourses={setCourses} setCurrentView={setCurrentView} setCurrentCourseIndex={setCurrentCourseIndex} />}
                
                {currentView === 'my-courses' && <MyCoursesDashboard courses={courses} setCurrentView={setCurrentView} setCurrentCourseIndex={setCurrentCourseIndex} />}
                
                {currentView === 'course-map' && currentCourseIndex !== null && (
                    <CourseMap 
                        course={courses[currentCourseIndex]} 
                        setCurrentView={setCurrentView} 
                        setCurrentSegment={setCurrentSegment} 
                    />
                )}
                
                {currentView === 'segment' && currentSegment && currentCourseIndex !== null && (
                    <SegmentViewer 
                        segment={currentSegment} 
                        courseIndex={currentCourseIndex}
                        setCurrentView={setCurrentView} 
                        setCourses={setCourses} 
                    />
                )}
                
                {currentView === 'codegraph-auth' && (
                    <CodeGraphAuth onUnlock={() => {
                        setIsGraphUnlocked(true);
                        setCurrentView('codegraph');
                    }} />
                )}

                {currentView === 'codegraph' && (
                    <div className="page-container" style={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
                        <h1 className="page-title">Code Graph</h1>
                        <div className="card" style={{ flex: 1, padding: 0, overflow: 'hidden', border: '1px solid #e2e8f0', borderRadius: '12px' }}>
                            <iframe 
                                src="graph.html" 
                                style={{ width: '100%', height: '100%', border: 'none' }}
                                title="Code Knowledge Graph"
                            />
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

// Render the App
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);

