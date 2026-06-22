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

function renderBoldText(text) {
    if (!text) return null;
    const parts = text.split(/\*\*(.*?)\*\*/g);
    return parts.map((part, index) => {
        if (index % 2 === 1) {
            return <strong key={index}>{part}</strong>;
        }
        return part;
    });
}

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

function ToastMessage({ message, type }) {
    if (!message) return null;
    const bg = type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#3b82f6';
    return (
        <div style={{
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            backgroundColor: bg,
            color: 'white',
            padding: '1rem',
            borderRadius: '8px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontWeight: 'bold',
            animation: 'fadeIn 0.3s ease-out'
        }}>
            {type === 'error' ? <i className="fa-solid fa-circle-xmark"></i> : 
             type === 'success' ? <i className="fa-solid fa-circle-check"></i> : 
             <i className="fa-solid fa-wand-magic-sparkles"></i>}
            {message}
        </div>
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

function CourseBuilder({ activeBuild, startBuild, uploadVideoAndBuild }) {
    const [inputType, setInputType] = useState('youtube');
    const [url, setUrl] = useState('');
    const [file, setFile] = useState(null);
    const [fastMode, setFastMode] = useState(false);

    const handleBuild = (e) => {
        e.preventDefault();
        if (inputType === 'youtube') {
            if (!url) return;
            startBuild(url, fastMode);
        } else {
            if (!file) return;
            uploadVideoAndBuild(file, fastMode);
        }
    };

    return (
        <div className="page-container">
            <h1 className="page-title">Course Builder</h1>
            <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
                <p className="mb-4" style={{ color: 'var(--text-muted)' }}>
                    Provide a YouTube link or upload a local video. We'll analyze the transcript, cut it into 3-minute segments, and generate quizzes.
                </p>
                
                <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
                    <button 
                        type="button" 
                        className={`btn ${inputType === 'youtube' ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => setInputType('youtube')}
                        style={{ flex: 1 }}
                        disabled={activeBuild?.active}
                    >
                        <i className="fa-brands fa-youtube mr-2"></i> YouTube Link
                    </button>
                    <button 
                        type="button" 
                        className={`btn ${inputType === 'upload' ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => setInputType('upload')}
                        style={{ flex: 1 }}
                        disabled={activeBuild?.active}
                    >
                        <i className="fa-solid fa-upload mr-2"></i> Upload Video
                    </button>
                </div>

                <form onSubmit={handleBuild}>
                    {inputType === 'youtube' ? (
                        <div className="form-group">
                            <label className="form-label">YouTube URL</label>
                            <input 
                                type="text" 
                                className="form-input" 
                                placeholder="https://www.youtube.com/watch?v=..."
                                value={url}
                                onChange={e => setUrl(e.target.value)}
                                disabled={activeBuild?.active}
                            />
                        </div>
                    ) : (
                        <div className="form-group">
                            <label className="form-label">Video File</label>
                            <input 
                                type="file" 
                                className="form-input" 
                                accept="video/mp4,video/webm,video/*"
                                onChange={e => setFile(e.target.files[0])}
                                disabled={activeBuild?.active}
                            />
                        </div>
                    )}
                    
                    <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <input 
                            type="checkbox" 
                            id="fastMode" 
                            checked={fastMode}
                            onChange={(e) => setFastMode(e.target.checked)}
                            disabled={activeBuild?.active}
                            style={{ width: '18px', height: '18px', accentColor: 'var(--primary)' }}
                        />
                        <label htmlFor="fastMode" style={{ margin: 0, cursor: 'pointer', color: 'var(--text-main)', fontWeight: '500' }}>
                            Fast Mode (Skip AI Evaluation)
                        </label>
                    </div>
                    {activeBuild.error && (
                        <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '1rem', borderRadius: '0.5rem', marginBottom: '1rem' }}>
                            <i className="fa-solid fa-circle-exclamation mr-2"></i> {activeBuild.error}
                        </div>
                    )}
                    
                    {activeBuild.active ? (
                        <div style={{ padding: '2rem', backgroundColor: '#f8fafc', borderRadius: '0.5rem', border: '1px solid #e2e8f0' }}>
                            <h3 style={{ fontSize: '1.2rem', color: 'var(--text-main)', marginBottom: '1.5rem', textAlign: 'center' }}>Initializing course...</h3>
                            
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem', fontSize: '0.95rem' }}>
                                <span style={{ color: 'var(--primary-dark)', fontWeight: 'bold' }}>
                                    <i className="fa-solid fa-circle-notch fa-spin" style={{ marginRight: '8px' }}></i>
                                    {activeBuild.message}
                                </span>
                                <span style={{ fontWeight: 'bold', color: 'var(--text-main)' }}>{activeBuild.progress}%</span>
                            </div>
                            
                            <div style={{ width: '100%', height: '12px', backgroundColor: '#e2e8f0', borderRadius: '6px', overflow: 'hidden', marginBottom: '0.5rem' }}>
                                <div style={{ height: '100%', width: `${activeBuild.progress}%`, backgroundColor: 'var(--primary)', transition: 'width 0.3s ease-out' }}></div>
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

function CourseMap({ course, setCurrentView, setCurrentSegment, activeBuild }) {
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
                {course.segments && course.segments.map((seg, idx) => {
                    const isProcessing = seg.status === 'locked' && activeBuild?.active && activeBuild?.youtube_id === course.youtube_id;
                    return (
                        <div key={seg.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', opacity: seg.status === 'locked' ? 0.6 : 1, position: 'relative', overflow: 'hidden' }}>
                            <div>
                                <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                                    {seg.status === 'locked' ? <i className="fa-solid fa-lock" style={{ color: 'var(--text-muted)', marginRight: '8px' }}></i> : <i className="fa-solid fa-unlock" style={{ color: 'var(--primary)', marginRight: '8px' }}></i>}
                                    {seg.title}
                                </h3>
                                <p style={{ color: 'var(--text-muted)' }}>Phase {idx + 1} - 3 Minute Video & Quiz</p>
                            </div>
                            {seg.status !== 'locked' ? (
                                <button className="btn btn-primary" onClick={() => {
                                    setCurrentSegment(seg);
                                    setCurrentView('segment');
                                }}>
                                    Start Segment <i className="fa-solid fa-arrow-right" style={{ marginLeft: '8px' }}></i>
                                </button>
                            ) : isProcessing ? (
                                <span style={{ color: 'var(--primary)', fontWeight: 'bold', fontSize: '0.9rem' }}>
                                    <i className="fa-solid fa-circle-notch fa-spin" style={{ marginRight: '8px' }}></i>
                                    Generating...
                                </span>
                            ) : null}
                        </div>
                    );
                })}
            </div>

            {activeBuild?.active && activeBuild?.youtube_id === course.youtube_id && (
                <div style={{ marginTop: '2rem', padding: '1.5rem', backgroundColor: '#f8fafc', borderRadius: '0.5rem', border: '1px solid #e2e8f0' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem', fontSize: '0.95rem' }}>
                        <span style={{ color: 'var(--primary-dark)', fontWeight: 'bold' }}>
                            <i className="fa-solid fa-circle-notch fa-spin" style={{ marginRight: '8px' }}></i>
                            {activeBuild.message}
                        </span>
                        <span style={{ fontWeight: 'bold', color: 'var(--text-main)' }}>{activeBuild.progress}%</span>
                    </div>
                    <div style={{ width: '100%', height: '8px', backgroundColor: '#e2e8f0', borderRadius: '4px', overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${activeBuild.progress}%`, backgroundColor: 'var(--primary)', transition: 'width 0.3s ease-out' }}></div>
                    </div>
                </div>
            )}

            {course.final_summary && (
                <div style={{ marginTop: '3rem', padding: '2rem', backgroundColor: '#ecfdf5', borderRadius: '1rem', border: '1px solid #10b981' }}>
                    <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#047857', marginBottom: '1rem', display: 'flex', alignItems: 'center' }}>
                        <i className="fa-solid fa-clipboard-check" style={{ marginRight: '12px' }}></i>
                        Important Points to Remember
                    </h2>
                    <div style={{ color: '#065f46', lineHeight: '1.6', fontSize: '1.05rem', whiteSpace: 'pre-line' }}>
                        {renderBoldText(course.final_summary)}
                    </div>
                </div>
            )}
        </div>
    );
}

function SegmentViewer({ segment, courseIndex, setCurrentView, setCourses }) {
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

    // Global background build state
    const [activeBuild, setActiveBuild] = useState({
        active: false,
        progress: 0,
        message: '',
        error: null,
        youtube_id: null
    });

    const [ollamaToast, setOllamaToast] = useState(null);
    const prevStatusRef = React.useRef('starting');

    useEffect(() => {
        let timeout;
        const pollOllama = async () => {
            try {
                const res = await fetch('/api/course/ollama-status');
                const data = await res.json();
                const status = data.status;
                const prev = prevStatusRef.current;
                
                if (status === 'failed' && prev !== 'failed') {
                    setOllamaToast({ message: 'Ai if failing to do the magic', type: 'error' });
                    setTimeout(() => setOllamaToast(null), 4000);
                } else if ((status === 'starting' || status === 'restarted') && prev === 'failed') {
                    setOllamaToast({ message: 'Ai is again ready to do the magic', type: 'success' });
                    setTimeout(() => setOllamaToast(null), 4000);
                } else if (status === 'running' && prev === 'starting') {
                    setOllamaToast({ message: 'Ai is doing the magic', type: 'info' });
                    setTimeout(() => setOllamaToast(null), 4000);
                }
                
                prevStatusRef.current = status;
            } catch (err) {
                // ignore
            }
            timeout = setTimeout(pollOllama, 5000);
        };
        pollOllama();
        return () => clearTimeout(timeout);
    }, []);

    const uploadVideoAndBuild = async (file, fastMode, retryCount = 0) => {
        setActiveBuild({ active: true, progress: 5, message: retryCount > 0 ? 'Retrying video upload...' : 'Uploading video...', error: null, youtube_id: null });
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const res = await fetch('/api/course/upload-video', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if (data.error) {
                if (retryCount < 1) {
                    setActiveBuild(prev => ({ ...prev, error: data.error + ' - Auto-restarting in 3s...', active: true }));
                    setTimeout(() => uploadVideoAndBuild(file, fastMode, retryCount + 1), 3000);
                } else {
                    setActiveBuild(prev => ({ ...prev, error: data.error, active: false }));
                }
                return;
            }
            startBuild(data.tempFilePath, fastMode, 0, true);
        } catch (err) {
            if (retryCount < 1) {
                setActiveBuild(prev => ({ ...prev, error: 'Upload failed: ' + err.message + ' - Auto-restarting in 3s...', active: true }));
                setTimeout(() => uploadVideoAndBuild(file, fastMode, retryCount + 1), 3000);
            } else {
                setActiveBuild(prev => ({ ...prev, error: 'Upload failed: ' + err.message, active: false }));
            }
        }
    };

    const startBuild = (url, fastMode, retryCount = 0, isLocal = false) => {
        if (!url) return;
        
        setActiveBuild({ active: true, progress: 0, message: retryCount > 0 ? 'Auto-restarting processing...' : 'Initializing...', error: null, youtube_id: null });
        
        const eventSource = new EventSource(`/api/course/stream-build?url=${encodeURIComponent(url)}&format=pdf&fastMode=${fastMode}`);
        let courseIdx = null;
        let specificErrorReceived = false;

        eventSource.addEventListener('course_init', (e) => {
            const data = JSON.parse(e.data);
            setCourses(prev => {
                const updated = [...prev, data];
                courseIdx = updated.length - 1;
                setCurrentCourseIndex(courseIdx);
                return updated;
            });
            setActiveBuild(prev => ({ ...prev, youtube_id: data.youtube_id, message: 'Extracting content...' }));
            setCurrentView('course-map');
        });

        eventSource.addEventListener('segment_done', (e) => {
            const segData = JSON.parse(e.data);
            setCourses(prev => {
                if (courseIdx === null) return prev;
                const newCourses = [...prev];
                const course = { ...newCourses[courseIdx] };
                course.segments = course.segments.map(s => s.id === segData.id ? segData : s);
                newCourses[courseIdx] = course;
                return newCourses;
            });
        });

        eventSource.addEventListener('course_done', (e) => {
            const data = JSON.parse(e.data);
            setCourses(prev => {
                if (courseIdx === null) return prev;
                const newCourses = [...prev];
                const course = { ...newCourses[courseIdx] };
                course.final_summary = data.final_summary;
                newCourses[courseIdx] = course;
                return newCourses;
            });
            setActiveBuild({ active: false, progress: 100, message: '', error: null, youtube_id: null });
            eventSource.close();
        });

        eventSource.addEventListener('progress', (e) => {
            const data = e.data;
            const splitIdx = data.indexOf(':');
            if (splitIdx !== -1) {
                const pct = parseInt(data.substring(0, splitIdx), 10);
                const msg = data.substring(splitIdx + 1);
                setActiveBuild(prev => ({ ...prev, progress: pct, message: msg }));
            }
        });

        eventSource.addEventListener('ping', (e) => {
            // Keep alive heartbeat, ignore
        });

        const handleFailure = (errorMsg) => {
            specificErrorReceived = true;
            eventSource.close();
            if (retryCount < 1) {
                setActiveBuild(prev => ({ ...prev, error: errorMsg + ' (Auto-restarting in 3s...)', active: true }));
                setTimeout(() => {
                    startBuild(url, fastMode, retryCount + 1, isLocal);
                }, 3000);
            } else {
                setActiveBuild(prev => ({ ...prev, error: errorMsg, active: false }));
            }
        };

        eventSource.addEventListener('result', (e) => {
            const data = JSON.parse(e.data);
            if (data.error) {
                handleFailure(data.error);
            }
        });

        eventSource.onerror = (err) => {
            if (!specificErrorReceived) {
                handleFailure('Connection to server lost or failed.');
            }
            eventSource.close();
        };
    };

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
                
                {currentView === 'builder' && <CourseBuilder activeBuild={activeBuild} startBuild={startBuild} uploadVideoAndBuild={uploadVideoAndBuild} />}
                
                {currentView === 'my-courses' && <MyCoursesDashboard courses={courses} setCurrentView={setCurrentView} setCurrentCourseIndex={setCurrentCourseIndex} />}
                
                {currentView === 'course-map' && currentCourseIndex !== null && (
                    <CourseMap 
                        course={courses[currentCourseIndex]} 
                        setCurrentView={setCurrentView} 
                        setCurrentSegment={setCurrentSegment} 
                        activeBuild={activeBuild}
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

