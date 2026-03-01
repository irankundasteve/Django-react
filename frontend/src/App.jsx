import { useEffect, useMemo, useState } from 'react';
import { Link, NavLink, Route, Routes } from 'react-router-dom';

const API_BASE = 'http://127.0.0.1:8000/api';

const navLinks = [
  ['/', 'Home'],
  ['/portfolio', 'Portfolio'],
  ['/about', 'About'],
  ['/services', 'Services'],
  ['/contact', 'Contact'],
];

function Layout({ children, contact }) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="app-shell">
      <header className="header">
        <Link to="/" className="logo" aria-label="Nanox home" onClick={() => setMenuOpen(false)}>
          NAN<span>O</span>X
        </Link>
        <button className="menu-toggle" aria-label="Toggle menu" onClick={() => setMenuOpen((prev) => !prev)}>☰</button>
        <nav className={`nav-links ${menuOpen ? 'open' : ''}`}>
          {navLinks.map(([to, label]) => (
            <NavLink key={to} to={to} onClick={() => setMenuOpen(false)} className={({ isActive }) => (isActive ? 'active' : '')}>
              {label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main>{children}</main>
      <footer className="footer">
        <div>
          <p><strong>Email:</strong> <a href={`mailto:${contact?.email}`}>{contact?.email}</a></p>
          <p><strong>Phone:</strong> <a href={`tel:${contact?.phone}`}>{contact?.phone}</a></p>
          <a href={contact?.facebook} target="_blank" rel="noreferrer">Facebook</a>
        </div>
        <div className="legal-links">
          <Link to="/privacy-policy">Privacy Policy</Link>
          <Link to="/terms-of-service">Terms of Service</Link>
        </div>
      </footer>
    </div>
  );
}

function CTAButtons() {
  return (
    <div className="cta-row">
      <Link className="btn" to="/portfolio">View Portfolio</Link>
      <Link className="btn" to="/contact">Book a Shoot</Link>
      <Link className="btn btn-outline" to="/about">Learn More</Link>
    </div>
  );
}

function Home({ images, aboutIntro }) {
  const [index, setIndex] = useState(0);
  useEffect(() => {
    if (!images.length) return;
    const timer = setInterval(() => setIndex((prev) => (prev + 1) % images.length), 5000);
    return () => clearInterval(timer);
  }, [images.length]);

  const current = images[index];
  const featured = images.slice(0, 4);

  return (
    <>
      <section className="hero" style={{ backgroundImage: `url(${current?.imageUrl})` }}>
        <div className="hero-overlay fade-in">
          <h1>Capturing Moments, Creating Stories</h1>
          <CTAButtons />
          <div className="carousel-controls">
            <button onClick={() => setIndex((index - 1 + images.length) % images.length)} aria-label="Previous">‹</button>
            <button onClick={() => setIndex((index + 1) % images.length)} aria-label="Next">›</button>
          </div>
        </div>
      </section>

      <section className="section fade-in">
        <h2>Featured Highlights</h2>
        <div className="grid">
          {featured.map((item) => (
            <Link to="/portfolio" className="card" key={item.id}>
              <img src={item.imageUrl} alt={item.title} />
              <div className="overlay"><strong>{item.title}</strong></div>
            </Link>
          ))}
        </div>
      </section>

      <section className="section about-snippet fade-in">
        <h2>About Nanox</h2>
        <p>{aboutIntro}</p>
        <Link className="btn" to="/about">Learn More</Link>
      </section>
    </>
  );
}

function Portfolio({ images }) {
  const [category, setCategory] = useState('All');
  const [selectedIndex, setSelectedIndex] = useState(null);
  const categories = useMemo(() => ['All', ...new Set(images.map((img) => img.category))], [images]);
  const filtered = category === 'All' ? images : images.filter((img) => img.category === category);
  const selectedItem = selectedIndex !== null ? filtered[selectedIndex] : null;

  const nextImage = () => setSelectedIndex((prev) => (prev + 1) % filtered.length);
  const prevImage = () => setSelectedIndex((prev) => (prev - 1 + filtered.length) % filtered.length);

  return (
    <section className="section fade-in">
      <h1>Portfolio</h1>
      <p className="subtext">Explore my photography collections</p>
      <div className="filters" role="tablist" aria-label="Portfolio categories">
        {categories.map((item) => (
          <button key={item} role="tab" aria-selected={item === category} className={item === category ? 'active' : ''} onClick={() => { setCategory(item); setSelectedIndex(null); }}>
            {item}
          </button>
        ))}
      </div>

      <div className="grid filter-fade">
        {filtered.map((item, idx) => (
          <article key={item.id} className="card" onClick={() => setSelectedIndex(idx)}>
            <img src={item.imageUrl} alt={item.title} />
            <div className="overlay"><strong>{item.title}</strong><span>{item.description}</span></div>
          </article>
        ))}
      </div>

      {selectedItem && (
        <div className="lightbox" onClick={() => setSelectedIndex(null)}>
          <button className="lightbox-close" aria-label="Close" onClick={() => setSelectedIndex(null)}>✕</button>
          <button className="lightbox-arrow left" aria-label="Previous image" onClick={(e) => { e.stopPropagation(); prevImage(); }}>‹</button>
          <div className="lightbox-content" onClick={(e) => e.stopPropagation()}>
            <img src={selectedItem.imageUrl} alt={selectedItem.title} />
            <div className="lightbox-caption"><h3>{selectedItem.title}</h3><p>{selectedItem.description}</p></div>
          </div>
          <button className="lightbox-arrow right" aria-label="Next image" onClick={(e) => { e.stopPropagation(); nextImage(); }}>›</button>
        </div>
      )}
    </section>
  );
}

function About({ about }) {
  return (
    <section className="section text-page fade-in">
      <h1>{about.headline}</h1>
      <p>{about.introParagraph}</p>
      <h2>Artistic Vision</h2>
      <p>{about.artisticVision}</p>
      <h2>Experience & Credentials</h2>
      <p>{about.experienceCredentials}</p>
      <Link className="btn" to="/contact">{about.ctaText || 'Book a Shoot'}</Link>
    </section>
  );
}

function Services({ services }) {
  const [open, setOpen] = useState(null);

  return (
    <section className="section text-page fade-in">
      <h1>Services</h1>
      <p className="subtext">Discover what I offer and how I work with clients</p>
      <div className="services-list">
        {services.map((service, idx) => (
          <article key={service.id || service.title} className="service-item">
            <button onClick={() => setOpen(open === idx ? null : idx)}>{service.title}<span>{open === idx ? '−' : '+'}</span></button>
            <div className={`service-content ${open === idx ? 'open' : ''}`}>
              <p>{service.description}</p>
              {service.details && <p>{service.details}</p>}
              {service.pricing && <p><strong>Pricing:</strong> {service.pricing}</p>}
            </div>
          </article>
        ))}
      </div>
      <Link className="btn" to="/contact">Book a Shoot</Link>
    </section>
  );
}

function Contact({ contact }) {
  const [form, setForm] = useState({ name: '', email: '', phone: '', message: '' });
  const [errors, setErrors] = useState({});
  const [status, setStatus] = useState('');

  const validate = () => {
    const nextErrors = {};
    if (!form.name.trim()) nextErrors.name = 'Name is required.';
    if (!form.email.trim()) nextErrors.email = 'Email is required.';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) nextErrors.email = 'Enter a valid email address.';
    if (!form.message.trim()) nextErrors.message = 'Message is required.';
    return nextErrors;
  };

  const onSubmit = async (event) => {
    event.preventDefault();
    const nextErrors = validate();
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) return;

    try {
      const response = await fetch(`${API_BASE}/contact/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Unable to send inquiry.');
      setStatus(data.message);
      setForm({ name: '', email: '', phone: '', message: '' });
      setErrors({});
    } catch (error) {
      setStatus(error.message);
    }
  };

  return (
    <section className="section contact-page fade-in">
      <h1>Contact Me</h1>
      <p className="subtext">I’d love to hear from you</p>
      <form onSubmit={onSubmit} noValidate>
        <label>Name *<input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} aria-invalid={Boolean(errors.name)} />{errors.name && <small className="error">{errors.name}</small>}</label>
        <label>Email *<input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} aria-invalid={Boolean(errors.email)} />{errors.email && <small className="error">{errors.email}</small>}</label>
        <label>Phone<input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></label>
        <label>Message *<textarea value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} aria-invalid={Boolean(errors.message)} />{errors.message && <small className="error">{errors.message}</small>}</label>
        <button className="btn" type="submit">Submit Inquiry</button>
      </form>
      <aside className="alt-contact">
        <h2>Alternate Contact</h2>
        <p><a href={`mailto:${contact?.email}`}>{contact?.email}</a></p>
        <p><a href={`tel:${contact?.phone}`}>{contact?.phone}</a></p>
      </aside>
      {status && <p className="status-msg">{status}</p>}
    </section>
  );
}

function Legal({ title, sections }) {
  return (
    <section className="section text-page fade-in">
      <h1>{title}</h1>
      {Object.entries(sections || {}).map(([heading, body]) => (
        <div key={heading} className="legal-section"><h2>{heading}</h2><p>{body}</p></div>
      ))}
    </section>
  );
}

export default function App() {
  const [site, setSite] = useState({});
  const [about, setAbout] = useState({});
  const [images, setImages] = useState([]);
  const [services, setServices] = useState([]);
  const [privacy, setPrivacy] = useState({});
  const [terms, setTerms] = useState({});

  useEffect(() => {
    fetch(`${API_BASE}/site-content/`).then((res) => res.json()).then(setSite).catch(() => setSite({}));
    fetch(`${API_BASE}/portfolio/`).then((res) => res.json()).then((res) => setImages(res.images || [])).catch(() => setImages([]));
    fetch(`${API_BASE}/about/`).then((res) => res.json()).then(setAbout).catch(() => setAbout({}));
    fetch(`${API_BASE}/services/`).then((res) => res.json()).then((res) => setServices(res.services || [])).catch(() => setServices([]));
    fetch(`${API_BASE}/privacy-policy/`).then((res) => res.json()).then(setPrivacy).catch(() => setPrivacy({}));
    fetch(`${API_BASE}/terms-of-service/`).then((res) => res.json()).then(setTerms).catch(() => setTerms({}));
  }, []);

  return (
    <Layout contact={site.contact}>
      <Routes>
        <Route path="/" element={<Home images={images} aboutIntro={about.introParagraph} />} />
        <Route path="/portfolio" element={<Portfolio images={images} />} />
        <Route path="/about" element={<About about={about} />} />
        <Route path="/services" element={<Services services={services} />} />
        <Route path="/contact" element={<Contact contact={site.contact} />} />
        <Route path="/privacy-policy" element={<Legal title="Privacy Policy" sections={privacy} />} />
        <Route path="/terms-of-service" element={<Legal title="Terms of Service" sections={terms} />} />
      </Routes>
    </Layout>
  );
}
