// Navbar component
function Navbar({ currentView, setCurrentView, onNavLinkClick }) {
 return (
 <nav className="navbar">
 <ul className="nav-links">
 <li
 className={currentView === "Home" ? "active" : ""}
 onClick={() => {
 setCurrentView("Home");
 onNavLinkClick();
 }}
 >
 Home
 </li>
 <li
 className={currentView === "Courses" ? "active" : ""}
 onClick={() => {
 setCurrentView("Courses");
 onNavLinkClick();
 }}
 >
 Courses
 </li>
 <li
 className={currentView === "Blog" ? "active" : ""}
 onClick={() => {
 setCurrentView("Blog");
 onNavLinkClick();
 }}
 >
 Blog
 </li>
 <li
 className={currentView === "Contact" ? "active" : ""}
 onClick={() => {
 setCurrentView("Contact");
 onNavLinkClick();
 }}
 >
 Contact
 </li>
 </ul>
 </nav>
 );
}

// Home component
function Home({ currentView, setCurrentView, courses }) {
 return (
 <div className="home-container">
 <section className="hero-section">
 <h1>Learning is key to your success</h1>
 </section>
 <section className="course-grid">
 {/* Course grid code goes here */}
 {courses.map((course) => (
 <div key={course.id} className="course-item">
 <h2>{course.title}</h2>
 <p>{course.description}</p>
 </div>
 ))}
 </section>
 </div>
 );
}