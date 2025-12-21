// ================= MODAL =================
const openModal = document.getElementById('openModal');
const closeModal = document.getElementById('closeModal');
const modal = document.getElementById('modal');
const phoneInput = document.getElementById("phone");
const phoneError = document.getElementById("phoneError");

openModal.addEventListener('click', () => {
  modal.classList.add('show');
  document.body.style.overflow = 'hidden';
});

function closeModalFunc(){
  modal.classList.remove('show');
  setTimeout(()=> document.body.style.overflow = '', 400);
}

closeModal.addEventListener('click', closeModalFunc);
window.addEventListener('click', e => {
  if(e.target === modal) closeModalFunc();
});


// ================= PHONE INPUT =================
phoneInput.addEventListener("input", () => {
  phoneInput.value = phoneInput.value.replace(/\D/g, "");
});


// ================= TOAST =================
function showToast(message, type="success"){
  const toast = document.getElementById("toast");
  const icons = {
    success:`<svg viewBox="0 0 24 24"><path d="M9 16.2l-3.5-3.5L4 14.2l5 5 11-11-1.5-1.5z"/></svg>`,
    warning:`<svg viewBox="0 0 24 24"><path d="M1 21h22L12 2 1 21z"/></svg>`
  };
  toast.innerHTML = icons[type] + message;
  toast.className = `toast show ${type}`;
  setTimeout(()=> toast.className = `toast ${type}`, 3200);
}


// ================= FORM AJAX =================
document.querySelector("form").addEventListener("submit", async function(e){
  e.preventDefault();

  if(phoneInput.value.length !== 9){
    phoneError.style.display = "block";
    return;
  }
  phoneError.style.display = "none";

  try{
    const res = await fetch("/submit", { method:"POST", body:new FormData(this) });
    res.ok
      ? showToast("Ma'lumotlar muvaffaqiyatli yuborildi","success")
      : showToast("Xatolik yuz berdi","warning");
  }catch{
    showToast("Server bilan aloqa yo‘q","warning");
  }

  this.reset();
  closeModalFunc();
});


// ================= PARTNERS SLIDER =================
// ================= PARTNERS AUTO SLIDE =================
const slider = document.querySelector(".partners-wrapper");
if (slider) {
  let speed = 5; // tezlik (kichikroq = sekinroq)
  let x = 0;

  // elementlarni klonlash (cheksiz loop uchun)
  function duplicatePartners() {
    const items = Array.from(slider.children);
    if (items.length === 0) return;

    // 1 ta bo‘lsa ham ishlashi uchun
    items.forEach(item => {
      const clone = item.cloneNode(true);
      slider.appendChild(clone);
    });
  }

  duplicatePartners();

  function animate() {
    x -= speed;

    // yarim uzunlikka yetganda qaytaramiz (jump YO‘Q)
    const halfWidth = slider.scrollWidth / 2;
    if (Math.abs(x) >= halfWidth) {
      x = 0;
    }

    slider.style.transform = `translateX(${x}px)`;
    requestAnimationFrame(animate);
  }

  animate();
}







// ================= BUYER =================
function addBuyer(name, phone){
  console.log(`Buyer: ${name}, ${phone}`);
  showToast(`${name} qo‘shildi`, "success");
}
