

const tooltips = document.querySelectorAll(".tooltip");
console.log(tooltips);

tooltips.forEach(function (element) {

  let tooltipSpan; // Zmienna zadeklarowana poza funkcjami

  element.addEventListener("mouseover", function () {
    let tooltipText = this.dataset.text;
    tooltipSpan = document.createElement("span");
    tooltipSpan.classList.add("tooltipText");
    tooltipSpan.innerText = tooltipText;
    this.appendChild(tooltipSpan);
  });

  element.addEventListener("mouseout", function () {
    if (tooltipSpan) {
      this.removeChild(tooltipSpan);
    }
  });
});

console.log("plik działa");