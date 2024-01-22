document.addEventListener("DOMContentLoaded", function () {
  const productSection = document.getElementById("productSection");

  const socket = io.connect(
    "http://" + document.domain + ":" + location.port
  );

  socket.on("product_data", function (data) {
    console.log("Received product data:", data);

    // Create and append new product cards
    data.products.forEach(function (product) {
      if (product[1] && product[2] && product[3]) {
        const card = document.createElement("div");
        card.className = "product-card";

        const productname = document.createElement("h3");
        productname.innerText = product[3];

        const link = document.createElement("a");
        link.href = product[0]; // Use correct index
        link.target = "_blank";

        const image = document.createElement("img");
        image.src = product[2]; // Use correct index
        image.alt = product[3]; // Use correct index

        const price = document.createElement("p");
        price.textContent = product[1]; // Use correct index

        link.appendChild(image);
        link.appendChild(productname);
        link.appendChild(price);
        card.appendChild(link);

        // Append the card to the product section
        productSection.appendChild(card);
      }
    });
  });

  const searchForm = document.getElementById("searchForm");

  searchForm.addEventListener("submit", function (event) {
    event.preventDefault();

    const formData = new FormData(searchForm);
    const productName = formData.get("productName");

    fetch("/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams(formData).toString(),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Search initiated:", data);
      })
      .catch((error) => {
        console.error("Error initiating search:", error);
      });
  });
});