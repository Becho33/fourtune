document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.querySelector(".nav-links");
  toggle?.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
    document.body.classList.toggle("menu-open", open);
  });

  const service = document.querySelector("#service");
  const birthFields = document.querySelector("#birthFields");
  const updateBirth = () => birthFields?.classList.toggle("visible", ["astrology", "four-pillars"].includes(service?.value));
  service?.addEventListener("change", updateBirth); updateBirth();

  const modal = document.querySelector("#enquiryModal");
  const close = modal?.querySelector(".modal-close");
  let maxScroll = window.scrollY;
  const dismissed = sessionStorage.getItem("akariEnquirySeen");
  const hideModal = () => { modal.hidden = true; sessionStorage.setItem("akariEnquirySeen", "1"); };
  close?.addEventListener("click", hideModal);
  modal?.addEventListener("click", e => { if (e.target === modal) hideModal(); });
  if (!dismissed) window.addEventListener("scroll", () => {
    const y = window.scrollY;
    const scrollable = Math.max(1, document.documentElement.scrollHeight - innerHeight);
    maxScroll = Math.max(maxScroll, y);
    const deepEnough = maxScroll >= 700 || maxScroll / scrollable >= .45;
    if (deepEnough && maxScroll - y > 45 && !sessionStorage.getItem("akariEnquirySeen")) {
      modal.hidden = false; sessionStorage.setItem("akariEnquirySeen", "1");
    }
  }, { passive: true });

  const enquiryForm = document.querySelector("#enquiryForm");
  enquiryForm?.addEventListener("submit", async e => {
    e.preventDefault();
    const error = enquiryForm.querySelector(".form-error");
    const data = Object.fromEntries(new FormData(enquiryForm));
    data.page_source = location.pathname;
    if (!data.email.trim() && !data.phone.trim()) { error.textContent = "Please provide an email address or telephone number."; return; }
    try {
      const response = await fetch("/api/enquiry", { method: "POST", headers: { "Content-Type": "application/json", "X-CSRFToken": data.csrf_token }, body: JSON.stringify(data) });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error);
      document.querySelector("#modalContent").innerHTML = '<div class="success-message"><p class="eyebrow">Message received</p><h2>Thank You</h2><p>Thank you for getting in touch. I have received your details and will contact you shortly.</p></div>';
    } catch (err) { error.textContent = err.message || "Something went wrong. Please try again."; }
  });
});
