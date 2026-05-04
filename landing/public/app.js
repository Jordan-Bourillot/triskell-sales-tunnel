// Triskell Sales Tunnel — landing client-side
// 1. Affiche un message si on n'est pas sur Windows
// 2. Animation logo subtile au survol

(function () {
  const ua = navigator.userAgent || "";
  const isWin = /Windows/i.test(ua);
  const dl = document.getElementById("download-btn");

  if (!isWin && dl) {
    dl.addEventListener("click", function (ev) {
      const ok = confirm(
        "Triskell Sales Tunnel est actuellement disponible uniquement pour Windows 10 / 11.\n\n" +
          "Veux-tu télécharger quand même ? (l'app ne se lancera probablement pas sur ton système)"
      );
      if (!ok) ev.preventDefault();
    });
  }

  // Effet hover logo
  const logo = document.querySelector(".logo-mark svg");
  if (logo) {
    logo.style.transition = "transform .4s cubic-bezier(.4,0,.2,1)";
    const card = document.querySelector(".card");
    if (card) {
      card.addEventListener("mouseenter", function () {
        logo.style.transform = "rotate(-8deg)";
      });
      card.addEventListener("mouseleave", function () {
        logo.style.transform = "rotate(0)";
      });
    }
  }
})();
