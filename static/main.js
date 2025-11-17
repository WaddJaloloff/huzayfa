// === MODAL FUNKSIYALARI ===
const openModal = document.getElementById('openModal');
const closeModal = document.getElementById('closeModal');
const modal = document.getElementById('modal');
const phoneInput = document.getElementById("phone");
const phoneError = document.getElementById("phoneError");

openModal.addEventListener('click', () => {
  modal.classList.add('show');
  document.body.style.overflow = 'hidden';
});

const closeModalFunc = () => {
  modal.classList.remove('show');
  setTimeout(() => document.body.style.overflow = '', 400);
};

closeModal.addEventListener('click', closeModalFunc);
window.addEventListener('click', e => { if(e.target === modal) closeModalFunc(); });


// === TELEFON RAQAM FAOLIYATI ===
phoneInput.addEventListener("input", () => {
  phoneInput.value = phoneInput.value.replace(/\D/g, "");
});


// === TOAST FUNKSIYASI ===
function showToast(message, type="success"){
  const toast = document.getElementById("toast");
  const icons = {
    success: `<svg viewBox="0 0 24 24"><path d="M9 16.2l-3.5-3.5L4 14.2l5 5 11-11-1.5-1.5z"></path></svg>`,
    warning: `<svg viewBox="0 0 24 24"><path d="M1 21h22L12 2 1 21z"></path></svg>`
  };
  toast.innerHTML = icons[type] + message;
  toast.className = "toast show " + type;
  setTimeout(() => toast.className = "toast " + type, 3200);
}


// === FORMNI AJAX ORQALI YUBORISH ===
document.querySelector("form").addEventListener("submit", async function(e){
  e.preventDefault();

  if(phoneInput.value.length !== 9){ 
    phoneError.style.display = "block"; 
    return; 
  }
  phoneError.style.display = "none";

  const formData = new FormData(this);
  try{
    const response = await fetch("/submit", { method:"POST", body:formData });
    if(response.ok){ 
      showToast("Ma'lumotlar muvaffaqiyatli yuborildi.", "success"); 
    } else { 
      showToast("Xatolik bo‘ldi, ammo ma'lumotlar qabul qilindi.", "warning"); 
    }
  } catch { 
    showToast("Serverga ulanib bo‘lmadi, ammo ma'lumotlar qabul qilindi.", "warning"); 
  }

  this.reset();
  closeModalFunc();
});


// === PARTNERS SLIDER ===
const slider = document.querySelector(".partners-wrapper");
if (slider) {

  const isMobile = window.matchMedia("(max-width: 768px)").matches;  // ← MUHIM QO‘SHIMCHA

  let scrollSpeed = 0.6; 
  let scrollPos = 5;
  const sliderItems = Array.from(slider.children);

  // Clone
  sliderItems.forEach(item => {
    const clone = item.cloneNode(true);
    slider.appendChild(clone);
  });

  const totalWidth = slider.scrollWidth / 2;

  let isDragging = false;
  let startX;
  let scrollLeft;

  function startDrag(e){
    isDragging = true;
    startX = (e.type.includes('touch') ? e.touches[0].pageX : e.pageX) - slider.offsetLeft;
    scrollLeft = slider.scrollLeft;
  }

  function endDrag(){ isDragging = false; }

  function dragMove(e){
    if(!isDragging) return;
    const x = (e.type.includes('touch') ? e.touches[0].pageX : e.pageX) - slider.offsetLeft;
    const walk = (x - startX) * 1;
    slider.scrollLeft = scrollLeft - walk;
    scrollPos = slider.scrollLeft;
  }

  slider.addEventListener('mousedown', startDrag);
  slider.addEventListener('mouseleave', endDrag);
  slider.addEventListener('mouseup', endDrag);
  slider.addEventListener('mousemove', dragMove);

  slider.addEventListener('touchstart', startDrag);
  slider.addEventListener('touchend', endDrag);
  slider.addEventListener('touchmove', dragMove);

  function autoScroll() {
    // MOBILDA AUTO-SLIDE O‘CHADI
    if(!isDragging && !isMobile){
      scrollPos += scrollSpeed;
      if(scrollPos >= totalWidth) scrollPos = 0;
      slider.scrollLeft = scrollPos;
    }
    requestAnimationFrame(autoScroll);
  }

  autoScroll();
}


// === BUYER FUNKSIYASI ===
function addBuyer(name, phone){
    console.log(`Buyer qo‘shildi: ${name}, ${phone}`);
    showToast(`${name} qo‘shildi`, "success");
}

