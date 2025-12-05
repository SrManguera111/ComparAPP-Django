// ==========================================
// VARIABLES PRINCIPALES
// ==========================================
const cartIcon = document.getElementById('cart-icon');
const cartSidebar = document.getElementById('cart-sidebar');
const cartOverlay = document.getElementById('cart-overlay');
const closeCart = document.getElementById('close-cart');
const cartItemsContainer = document.getElementById('cart-items');
const cartTotalElement = document.getElementById('cart-total');
const cartCountElement = document.getElementById('cart-count');

// Variables del QR y Checkout
const btnCheckout = document.querySelector('.btn-checkout'); 
const qrModal = document.getElementById('qr-modal');
const qrContainer = document.getElementById('qrcode-container');
const closeQrBtn = document.getElementById('close-qr');
const finishOrderBtn = document.getElementById('btn-finish-order');

// ==========================================
// CONFIGURACIÓN DE NÚMEROS WHATSAPP (POR LOCAL)
// ==========================================
const numerosWSP = {
    "Castaño":   "56991399444",  
    "Foodtruck": "56998658056",  
    "Casino":    "56923915950",  
    "General":   "56991399444"   
};

let cart = JSON.parse(localStorage.getItem('cart')) || [];

// ==========================================
// LÓGICA DEL CARRITO (ABRIR/CERRAR/RENDERIZAR)
// ==========================================

if (cartIcon) {
    cartIcon.addEventListener('click', () => {
        cartSidebar.classList.add('active');
        cartOverlay.classList.add('active');
    });
}
if (closeCart) {
    closeCart.addEventListener('click', () => {
        cartSidebar.classList.remove('active');
        cartOverlay.classList.remove('active');
    });
}
if (cartOverlay) {
    cartOverlay.addEventListener('click', () => {
        cartSidebar.classList.remove('active');
        cartOverlay.classList.remove('active');
    });
}

// Función principal para renderizar el carrito
function updateCart() {
    if (!cartItemsContainer) return;

    cartItemsContainer.innerHTML = '';
    let total = 0;
    let count = 0;

    cart.forEach((item, index) => {
        total += item.price * item.quantity;
        count += item.quantity;

        const cartItem = document.createElement('div');
        cartItem.classList.add('cart-item');
        cartItem.innerHTML = `
            <div class="cart-item-info">
                <h4>${item.name}</h4>
                <p>$${item.price} x ${item.quantity} = $${item.price * item.quantity}</p>
            </div>
            <span class="cart-item-remove" data-index="${index}">×</span>
        `;
        cartItemsContainer.appendChild(cartItem);
    });

    if (cartTotalElement) cartTotalElement.innerText = total.toLocaleString('es-CL'); 
    if (cartCountElement) cartCountElement.innerText = count;

    localStorage.setItem('cart', JSON.stringify(cart));
    
    if (cart.length === 0) {
        cartItemsContainer.innerHTML = '<p>Tu carrito está vacío</p>';
    }

    document.querySelectorAll('.cart-item-remove').forEach(button => {
        button.addEventListener('click', (e) => {
            const indexToRemove = e.target.dataset.index;
            cart.splice(indexToRemove, 1);
            updateCart();
        });
    });
}

// ==========================================
// NUEVA FUNCIÓN: MOSTRAR TOAST (Notificación)
// ==========================================
function launchToast(mensaje) {
    var x = document.getElementById("toast");
    var desc = document.getElementById("desc");
    
    if (mensaje && desc) desc.innerText = mensaje;

    if(x) x.className = "show";

    setTimeout(function(){ 
        if(x) x.className = x.className.replace("show", ""); 
    }, 3000);
}

// ==========================================
// LOGICA "AGREGAR AL CARRITO" (CON VENDEDORES)
// ==========================================
document.addEventListener('click', (e) => {
    const button = e.target.closest('.add-to-cart');

    if (button) {
        e.preventDefault();
        
        const id = button.dataset.id;
        const baseName = button.dataset.name;
        const price = parseInt(button.dataset.price);
        const vendor = button.dataset.vendor; 

        let uniqueId = id;
        let fullName = baseName;

        if (vendor) {
            uniqueId = `${id}-${vendor}`; 
            fullName = `${baseName} (${vendor})`; 
        }

        const existingItem = cart.find(item => (item.uniqueId || item.id) === uniqueId);

        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            cart.push({ 
                uniqueId: uniqueId, 
                id: id,             
                name: fullName, 
                price: price, 
                quantity: 1,
                vendor: vendor || 'General' 
            });
        }

        updateCart();
        launchToast(`Se agregó ${fullName} al carrito`);
    }
});

updateCart();

// ==========================================
// LÓGICA DE SWIPERS (SLIDERS) Y TABS
// ==========================================

if (document.querySelector(".mySwiper-1")) {
    var swiper1 = new Swiper(".mySwiper-1",{
        slidesPerView:1,
        spaceBetween: 30,
        loop:true,
        pagination:{
            el:".swiper-pagination",
            clickable:true,
        },
        navigation:{
            nextEl:".swiper-button-next",
            prevEl:".swiper-button-prev",
        }
    });
}

if (document.querySelector(".mySwiper-2")) {
    var swiper2 = new Swiper(".mySwiper-2",{
        slidesPerView:3,
        spaceBetween: 20,
        loop:true,
        loopFillGroupWithBlank:true,
        navigation:{
            nextEl:".swiper-button-next",
            prevEl:".swiper-button-prev",
        },
        breakpoints : {
            0: { slidesPerView:1 },
            520: { slidesPerView:2 },
            950: { slidesPerView:3 },
        }
    });
}

let tabInputs = document.querySelectorAll(".tabInput");

if (tabInputs.length > 0) {
    tabInputs.forEach(function(input){
        input.addEventListener('change',function(){
            let id = input.value; 
            let thisSwiper = document.getElementById('swiper' + id);
            if(thisSwiper && thisSwiper.swiper){
                thisSwiper.swiper.update();
            }
        })
    });
}

// =====================================================
// LÓGICA DE CHECKOUT: ENVIAR A DJANGO Y GENERAR MÚLTIPLES QRs
// =====================================================

if (btnCheckout) { 
    btnCheckout.addEventListener('click', () => {
        if (cart.length === 0) {
            alert("Tu carrito está vacío");
            return;
        }

        let total = 0;
        cart.forEach(item => { total += item.price * item.quantity; });

        fetch('/procesar_orden/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'carrito': cart,
                'total': total
            })
        })
        .then(response => {
            if (response.status === 401 || response.url.includes('/login/')) {
                alert("Debes iniciar sesión para realizar una compra.");
                window.location.href = "/login/"; 
                return null; 
            }
            return response.json();
        })
        .then(data => {
            if (data && data.status === 'success') {
                console.log("Orden guardada ID:", data.orden_id);
                generarMultiplesQR(cart, data.orden_id);
                
            } else if (data) {
                alert("Error al guardar orden: " + data.message);
            }
        })
        .catch(error => {
            console.error("Error en la petición:", error);
            alert("Ocurrió un error de conexión.");
        });
    });
}

// Función para generar MÚLTIPLES QRs (CORREGIDA)
function generarMultiplesQR(cart, ordenId) {
    if (!qrContainer) return;
    
    qrContainer.innerHTML = "";
    qrContainer.classList.add('qr-content'); 

    // Agrupar productos por Vendedor
    const grupos = {};
    cart.forEach(item => {
        const vendedor = item.vendor || "General";
        if (!grupos[vendedor]) {
            grupos[vendedor] = [];
        }
        grupos[vendedor].push(item);
    });

    for (const [vendedor, items] of Object.entries(grupos)) {
        
        let subtotalVendedor = 0;
        let mensaje = `ORDEN #${ordenId} - ${vendedor.toUpperCase()}\n\n`;
        
        items.forEach(item => {
            let totalItem = item.price * item.quantity;
            subtotalVendedor += totalItem;
            let nombreLimpio = item.name.replace(` (${vendedor})`, '');
            mensaje += `- ${item.quantity} x ${nombreLimpio} ($${totalItem})\n`;
        });

        mensaje += `\nTOTAL A PAGAR: $${subtotalVendedor.toLocaleString('es-CL')}`;

        // === CORRECCIÓN AQUÍ ===
        // Seleccionamos el número correcto
        const numeroDestino = numerosWSP[vendedor] || numerosWSP["General"];

        const bloqueQR = document.createElement('div');
        bloqueQR.className = 'qr-block'; 
        
        const titulo = document.createElement('h3');
        titulo.innerText = `Ticket: ${vendedor}`;
        titulo.style.marginBottom = "10px";
        titulo.style.color = "#DB241B";
        
        const divParaElQR = document.createElement('div');
        divParaElQR.style.display = "flex";
        divParaElQR.style.justifyContent = "center";
        
        bloqueQR.appendChild(titulo);
        bloqueQR.appendChild(divParaElQR);
        qrContainer.appendChild(bloqueQR);

        // === CORRECCIÓN AQUÍ TAMBIÉN ===
        // Usamos 'numeroDestino' en lugar de la variable antigua
        const linkWhatsApp = `https://wa.me/${numeroDestino}?text=${encodeURIComponent(mensaje)}`;
        
        new QRCode(divParaElQR, {
            text: linkWhatsApp,
            width: 150, 
            height: 150,
            colorDark : "#000000",
            colorLight : "#ffffff",
            correctLevel : QRCode.CorrectLevel.M
        });
    }

    if (qrModal) qrModal.classList.add('active');
    if (cartSidebar) cartSidebar.classList.remove('active');
    if (cartOverlay) cartOverlay.classList.remove('active');
}

if (closeQrBtn) {
    closeQrBtn.addEventListener('click', () => {
        qrModal.classList.remove('active');
    });
}

if (finishOrderBtn) {
    finishOrderBtn.addEventListener('click', () => {
        qrModal.classList.remove('active');
        cart = []; 
        localStorage.removeItem('cart'); 
        updateCart(); 
        alert("¡Gracias por tu compra! Tu orden ha sido registrada.");
    });
}

// Función genérica para ir a comprar a CUALQUIER categoría
function irAComprar(idPestana) {
    
    const tabSeleccionada = document.getElementById(idPestana);
    
    if (tabSeleccionada) {
        tabSeleccionada.checked = true;
        tabSeleccionada.dispatchEvent(new Event('change'));
    }

    const catalogo = document.getElementById('catalogo');
    if (catalogo) {
        catalogo.scrollIntoView({ behavior: 'smooth' });
    }
}