import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';

const WHATSAPP_NUMBER = '970592630530';
const EMAIL = 'ebantbaeil2004@gmail.com';
const INSTAGRAM_URL = 'https://www.instagram.com/smartdev1.ai/';

export default function ContactPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [subject, setSubject] = useState('General inquiry');
  const [message, setMessage] = useState('');

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const body = encodeURIComponent(
      `Name: ${name}\nEmail: ${email}\nSubject: ${subject}\n\n${message}`,
    );
    const mailSubject = encodeURIComponent(`[Talentscope] ${subject}`);
    window.location.href = `mailto:${EMAIL}?subject=${mailSubject}&body=${body}`;
  }

  const whatsappUrl = `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(
    'Hi Eban, I need help with Talentscope.',
  )}`;

  return (
    <div className="bg-gradient-to-b from-brand-50/30 via-white to-white">
      {/* ==================== HEADER ==================== */}
      <section className="relative overflow-hidden">
        <div
          aria-hidden
          className="absolute -top-40 -right-40 h-[500px] w-[500px] rounded-full bg-brand-300/20 blur-3xl"
        />
        <div className="relative mx-auto max-w-7xl px-6 pt-20 pb-12 lg:px-8 lg:pt-28">
          <div className="mx-auto max-w-3xl text-center space-y-4">
            <div className="pill-badge mx-auto">
              <i className="fa-solid fa-headset text-brand-600" />
              <span className="text-brand-700">We're here to help</span>
            </div>
            <h1 className="font-display text-4xl font-bold tracking-tight text-ink-900 sm:text-5xl">
              Get in <span className="gradient-text">touch</span>
            </h1>
            <p className="text-lg text-ink-600">
              Have a question, a bug to report, or a feature request?
              Reach out through any channel below.
            </p>
          </div>
        </div>
      </section>

      {/* ==================== CONTACT CARDS ==================== */}
      <section className="mx-auto max-w-7xl px-6 pb-16 lg:px-8">
        <div className="grid gap-6 md:grid-cols-3">
          <ContactCard
            icon="fa-brands fa-whatsapp"
            iconBg="bg-[#25D366]"
            title="WhatsApp"
            description="Fastest way to reach us. Typical reply within 1 hour."
            cta="Open WhatsApp"
            href={whatsappUrl}
            external
          />
          <ContactCard
            icon="fa-solid fa-envelope"
            iconBg="bg-brand-600"
            title="Email"
            description="Detailed questions, bug reports, or formal requests."
            cta="Send an email"
            href={`mailto:${EMAIL}`}
            external
          />
          <ContactCard
            icon="fa-brands fa-instagram"
            iconBg="bg-gradient-to-tr from-[#F58529] via-[#DD2A7B] to-[#8134AF]"
            title="Instagram"
            description="Follow for updates, tips, and behind-the-scenes."
            cta="Follow us"
            href={INSTAGRAM_URL}
            external
          />
        </div>
      </section>

      {/* ==================== FORM ==================== */}
      <section className="mx-auto max-w-4xl px-6 pb-24 lg:px-8">
        <div className="rounded-3xl border border-ink-100 bg-white p-8 shadow-soft-lg sm:p-12">
          <div className="mb-8 space-y-2">
            <h2 className="font-display text-2xl font-bold text-ink-900">
              Send us a message
            </h2>
            <p className="text-sm text-ink-500">
              Fill out the form and we'll get back to you as soon as possible.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid gap-5 sm:grid-cols-2">
              <Field
                id="name"
                label="Your name"
                type="text"
                value={name}
                onChange={setName}
                placeholder="John Doe"
                required
              />
              <Field
                id="email"
                label="Your email"
                type="email"
                value={email}
                onChange={setEmail}
                placeholder="you@example.com"
                required
              />
            </div>

            <div className="space-y-1.5">
              <label htmlFor="subject" className="label">
                Subject
              </label>
              <select
                id="subject"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="input"
              >
                <option>General inquiry</option>
                <option>Report a bug</option>
                <option>Feature request</option>
                <option>Organization subscription</option>
                <option>Other</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label htmlFor="message" className="label">
                Message
              </label>
              <textarea
                id="message"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={6}
                className="input resize-none"
                placeholder="Tell us more about your request..."
                required
              />
            </div>

            <button type="submit" className="btn btn-primary btn-lg w-full sm:w-auto">
              <i className="fa-solid fa-paper-plane text-sm" />
              Send message
            </button>
          </form>
        </div>
      </section>

      {/* ==================== BACK HOME ==================== */}
      <section className="mx-auto max-w-7xl px-6 pb-24 text-center lg:px-8">
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-sm font-semibold text-brand-600 hover:text-brand-700"
        >
          <i className="fa-solid fa-arrow-left text-xs" />
          Back to home
        </Link>
      </section>
    </div>
  );
}

// ============================================================
// Components
// ============================================================
function ContactCard({
  icon,
  iconBg,
  title,
  description,
  cta,
  href,
  external,
}: {
  icon: string;
  iconBg: string;
  title: string;
  description: string;
  cta: string;
  href: string;
  external?: boolean;
}) {
  return (
    <a
      href={href}
      {...(external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}
      className="group rounded-3xl border border-ink-100 bg-white p-6 transition-all hover:-translate-y-1 hover:border-brand-200 hover:shadow-soft-lg"
    >
      <div className={`grid h-14 w-14 place-items-center rounded-2xl text-white text-xl shadow-soft-md ${iconBg}`}>
        <i className={icon} />
      </div>
      <h3 className="mt-5 font-display text-lg font-bold text-ink-900">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-ink-600">{description}</p>
      <p className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-brand-600 transition-transform group-hover:translate-x-1">
        {cta}
        <i className="fa-solid fa-arrow-right text-xs" />
      </p>
    </a>
  );
}

function Field({
  id,
  label,
  type,
  value,
  onChange,
  placeholder,
  required,
}: {
  id: string;
  label: string;
  type: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  required?: boolean;
}) {
  return (
    <div className="space-y-1.5">
      <label htmlFor={id} className="label">
        {label}
      </label>
      <input
        id={id}
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        required={required}
        className="input"
      />
    </div>
  );
}
