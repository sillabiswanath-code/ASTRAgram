Here are the JavaScript codes for the 'Navbar' and 'Home' React components:

// Navbar component
function Navbar() {
 return (
 <nav>
 <ul>
 <li><a href="#">Home</a></li>
 <li><a href="#">Courses</a></li>
 <li><a href="#">Blog</a></li>
 <li><a href="#">Contact</a></li>
 </ul>
 </nav>
 );
}
// Home component
function Home() {
 return (
 <div className="home-container">
 <section className="hero">
 <h1>Learning is key to your success</h1>
 </section>
 <section className="course-grid">
 {/* Course grid code goes here */}
 </section>
 </div>
 );
}
