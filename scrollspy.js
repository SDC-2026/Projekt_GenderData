document.addEventListener("DOMContentLoaded", () => {

  const navLinks = document.querySelectorAll(".section-nav a");

  // Zuordnung deiner Navigation zu den Abschnitten
  const sections = [
    { id: "introduction", nav: "introduction" },
    { id: "research-question", nav: "research-question" },

    // Alles hiervon gehört zu "Pipeline"
    { id: "pipeline-overview", nav: "pipeline-overview" },
    { id: "data-cleaning", nav: "pipeline-overview" },
    { id: "identity-detection", nav: "pipeline-overview" },
    { id: "relationship-inference", nav: "pipeline-overview" },
    { id: "manual-review", nav: "pipeline-overview" },
    { id: "load-final-dataset", nav: "pipeline-overview" },

    // Alles hiervon gehört zu "Analysis"
    { id: "dataset-overview", nav: "dataset-overview" },
    { id: "distribution-of-lgbtq-identities", nav: "dataset-overview" },
    { id: "treemap-overview", nav: "dataset-overview" },
    { id: "lgbtq-representation-over-time", nav: "dataset-overview" },
    { id: "development-across-years", nav: "dataset-overview" },

    // Findings
    { id: "key-findings", nav: "key-findings" },
    { id: "interpretation-of-results", nav: "key-findings" },
    { id: "methodological-reflection", nav: "key-findings" },
    { id: "limitations", nav: "key-findings" },

    // Conclusion
    { id: "conclusion", nav: "conclusion" },
    { id: "reproducibility", nav: "conclusion" },
    { id: "references", nav: "conclusion" }
  ];

  const sectionElements = sections
    .map(s => ({
      nav: s.nav,
      element: document.getElementById(s.id)
    }))
    .filter(s => s.element);

  function updateActiveSection() {

    let current = sectionElements[0];

    sectionElements.forEach(section => {

      if (window.scrollY >= section.element.offsetTop - 140) {
        current = section;
      }

    });

    navLinks.forEach(link => link.classList.remove("active"));

    const active = document.querySelector(
      `.section-nav a[href="#${current.nav}"]`
    );

    if (active) {
      active.classList.add("active");
    }
  }

  window.addEventListener("scroll", updateActiveSection);

  updateActiveSection();

});