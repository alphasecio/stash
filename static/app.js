function copyUrl() {
  const btn = document.getElementById("copyBtn");
  
  // Use the browser's current URL directly
  navigator.clipboard.writeText(window.location.href).then(() => {
    const originalText = btn.innerText;
    btn.innerText = "Copied!";
    setTimeout(() => {
      btn.innerText = originalText;
    }, 2000);
  });
}
