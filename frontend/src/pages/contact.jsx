
import { useState } from "react";

function Contact() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    subject: "",
    message: "",
  });

  const [notice, setNotice] = useState("");

  const handleChange = (event) => {
    setForm({
      ...form,
      [event.target.name]: event.target.value,
    });
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    setNotice(
      "The contact form is ready. Message delivery will be added soon."
    );
  };

  return (
    <main className="main-content">
      <section className="page-heading">
        <h1>Contact RealestateAI</h1>

        <p>
          Have questions, feedback, or suggestions?
          We'd love to hear from you.
        </p>
      </section>

      <form className="contact-form" onSubmit={handleSubmit}>
        <label htmlFor="name">Full Name</label>
        <input
          id="name"
          name="name"
          value={form.name}
          onChange={handleChange}
          required
        />

        <label htmlFor="email">Email Address</label>
        <input
          id="email"
          name="email"
          type="email"
          value={form.email}
          onChange={handleChange}
          required
        />

        <label htmlFor="subject">Subject</label>
        <input
          id="subject"
          name="subject"
          value={form.subject}
          onChange={handleChange}
          required
        />

        <label htmlFor="message">Message</label>
        <textarea
          id="message"
          name="message"
          rows="6"
          value={form.message}
          onChange={handleChange}
          required
        />

        <button type="submit">Send Message</button>

        {notice && <p role="status">{notice}</p>}
      </form>
    </main>
  );
}

export default Contact;
