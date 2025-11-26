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

// Tu número de teléfono para WhatsApp
const tuNumeroWhatsApp = "56991399444"; 

let cart = JSON.parse(localStorage.getItem('cart')) || [];

// ==========================================
// LÓGICA DEL CARRITO (ABRIR/CERRAR/RENDERIZAR)
// ==========================================

// Abrir y Cerrar Carrito
cartIcon.addEventListener('click', () => {
    cartSidebar.classList.add('active');
    cartOverlay.classList.add('active');
});
closeCart.addEventListener('click', () => {
    cartSidebar.classList.remove('active');
    cartOverlay.classList.remove('active');
});
cartOverlay.addEventListener('click', () => {
    cartSidebar.classList.remove('active');
    cartOverlay.classList.remove('active');
});

// Función principal para renderizar el carrito
function updateCart() {
    // 1. Limpiar vista actual
    cartItemsContainer.innerHTML = '';
    let total = 0;
    let count = 0;

    // 2. Recorrer el carrito y crear HTML
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

    // 3. Actualizar totales en pantalla
    cartTotalElement.innerText = total.toLocaleString('es-CL'); 
    cartCountElement.innerText = count;

    // 4. Guardar en LocalStorage
    localStorage.setItem('cart', JSON.stringify(cart));
    
    // 5. Si está vacío mostrar mensaje
    if (cart.length === 0) {
        cartItemsContainer.innerHTML = '<p>Tu carrito está vacío</p>';
    }

    // 6. Activar botones de eliminar
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
    
    // Actualizar el texto de la notificación
    if (mensaje) desc.innerText = mensaje;

    // Mostrar
    x.className = "show";

    // Ocultar después de 3 segundos
    setTimeout(function(){ 
        x.className = x.className.replace("show", ""); 
    }, 3000);
}

// ==========================================
// LOGICA "AGREGAR AL CARRITO" (MODIFICADA)
// ==========================================
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('add-to-cart')) {
        e.preventDefault();
        
        const id = e.target.dataset.id;
        const name = e.target.dataset.name;
        const price = parseInt(e.target.dataset.price);

        // Buscar si ya existe el producto en el carrito
        const existingItem = cart.find(item => item.id === id);

        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            cart.push({ id, name, price, quantity: 1 });
        }

        // Actualizamos los números del carrito
        updateCart();

        // --- CAMBIO IMPORTANTE ---
        // Ya NO abrimos el sidebar automáticamente.
        // En su lugar, llamamos a la notificación Toast.
        launchToast(`Se agregó ${name} al carrito`);
    }
});

// Inicializar carrito al cargar la página
updateCart();

// ==========================================
// LÓGICA DE SWIPERS (SLIDERS) Y TABS
// ==========================================

var swiper = new Swiper(".mySwiper-1",{
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

var swiper = new Swiper(".mySwiper-2",{
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

let tabInputs = document.querySelectorAll(".tabInput");

tabInputs.forEach(function(input){
    input.addEventListener('change',function(){
        let id = input.value; 
        let thisSwiper = document.getElementById('swiper' + id);
        if(thisSwiper && thisSwiper.swiper){
            thisSwiper.swiper.update();
        }
    })
})

// =====================================================
// LÓGICA DE CHECKOUT: ENVIAR A DJANGO Y GENERAR QR
// =====================================================

btnCheckout.addEventListener('click', () => {
    if (cart.length === 0) {
        alert("Tu carrito está vacío");
        return;
    }

    // 1. Calcular el total antes de enviar
    let total = 0;
    cart.forEach(item => { total += item.price * item.quantity; });

    // 2. Enviar datos al Backend (Django)
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
        // Si el usuario no está logueado (Error 401 o redirección al login)
        if (response.status === 401 || response.url.includes('/login/')) {
            alert("Debes iniciar sesión para realizar una compra.");
            window.location.href = "/login/"; // Redirige al login
            return null; 
        }
        return response.json();
    })
    .then(data => {
        if (data && data.status === 'success') {
            // ¡Éxito! Guardamos la orden en la BD.
            // Ahora generamos el QR con el ID real de la orden.
            console.log("Orden creada exitosamente. ID:", data.orden_id);
            generarQR(cart, total, data.orden_id);
            
        } else if (data) {
            alert("Hubo un problema al guardar tu orden: " + data.message);
        }
    })
    .catch(error => {
        console.error("Error en la petición:", error);
        alert("Ocurrió un error de conexión.");
    });
});

// Función auxiliar para generar el QR (Solo se llama si Django responde OK)
function generarQR(cart, total, ordenId) {
    // Crear el mensaje para WhatsApp
    let mensaje = `¡Hola! Acabo de hacer el Pedido Web #${ordenId} en Food Finder:\n\n`;
    
    cart.forEach(item => {
        let subtotal = item.price * item.quantity;
        mensaje += `- ${item.quantity} x ${item.name} ($${subtotal})\n`;
    });

    mensaje += `\n*TOTAL A PAGAR: $${total.toLocaleString('es-CL')}*`;
    mensaje += "\n\nQuedo atento a la confirmación.";

    // Crear link
    const linkWhatsApp = `https://wa.me/${tuNumeroWhatsApp}?text=${encodeURIComponent(mensaje)}`;

    // Limpiar y generar QR
    qrContainer.innerHTML = "";
    new QRCode(qrContainer, {
        text: linkWhatsApp,
        width: 200,
        height: 200,
        colorDark : "#000000",
        colorLight : "#ffffff",
        correctLevel : QRCode.CorrectLevel.H
    });

    // Mostrar Modal y cerrar carrito
    qrModal.classList.add('active');
    cartSidebar.classList.remove('active');
    cartOverlay.classList.remove('active');
}

// Cerrar el modal del QR (X)
closeQrBtn.addEventListener('click', () => {
    qrModal.classList.remove('active');
});

// Botón "Cerrar y Limpiar": Finaliza todo el proceso
finishOrderBtn.addEventListener('click', () => {
    qrModal.classList.remove('active');
    cart = []; // Vaciar variable
    localStorage.removeItem('cart'); // Vaciar memoria local
    updateCart(); // Actualizar visualmente
    alert("¡Gracias por tu compra! Tu orden ha sido registrada.");
});