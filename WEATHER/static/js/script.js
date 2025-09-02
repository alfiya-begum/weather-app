document.addEventListener("DOMContentLoaded", () => {
  console.log("Weather app loaded 🌦");

  document.querySelectorAll("button").forEach(btn => {
    btn.addEventListener("click", function (e) {
      let ripple = document.createElement("span");
      ripple.classList.add("ripple");
      this.appendChild(ripple);

      let x = e.clientX - this.offsetLeft;
      let y = e.clientY - this.offsetTop;
      ripple.style.left = `${x}px`;
      ripple.style.top = `${y}px`;

      setTimeout(() => ripple.remove(), 600);
    });
  });
});
