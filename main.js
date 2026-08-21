document.addEventListener('DOMContentLoaded', () => {
    // --- APP STATE ---
    const state = {
        movies: [],
        topMovies: [],
        user: null,
        selectedMovie: null,
        selectedShowtime: null,
        selectedSeats: new Set(),
        currentStep: 1,
        favorites: [],
        snacksTotal: 0,
        seatTotal: 0,
        snacks: { popcorn: 0, coke: 0, nachos: 0 },
        activeFilter: 'All'
    };

    // --- ELEMENTS ---
    const loginNavBtn = document.getElementById('login-nav-btn');
    const loggedInState = document.getElementById('logged-in-state');
    const userNameDisplay = document.getElementById('user-display-name');
    const logoutBtn = document.getElementById('logout-btn');
    const authModal = document.getElementById('auth-modal');
    const bookingModal = document.getElementById('booking-modal');
    const closeModal = document.getElementById('close-modal');
    const topMoviesGrid = document.getElementById('top-movies-grid');
    const languageSectionsContainer = document.getElementById('language-sections-container');
    const dashboardTickets = document.getElementById('dashboard-tickets');
    const globalSearch = document.getElementById('global-search');
    const searchResults = document.getElementById('search-results');

    // --- INITIALIZATION ---
    const init = async () => {
        await fetchUser();
        await fetchMovies();
        renderHome();
        setupNav();
        setupSearch();
        setupThemeToggle();
        setupAdminMovieAdd();
    };

    // --- THEME TOGGLE ---
    const setupThemeToggle = () => {
        const themeBtn = document.getElementById('theme-btn');
        if (!themeBtn) return;
        
        // Load preference
        const currentTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', currentTheme);
        themeBtn.textContent = currentTheme === 'dark' ? '☀️' : '🌙';

        themeBtn.onclick = () => {
            const current = document.documentElement.getAttribute('data-theme');
            const target = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', target);
            localStorage.setItem('theme', target);
            themeBtn.textContent = target === 'dark' ? '☀️' : '🌙';
        };
    };

    // --- AUTH LOGIC ---
    const fetchUser = async () => {
        try {
            const res = await fetch('/api/me');
            if (res.ok) {
                const data = await res.json();
                if (data.success) {
                    await updateUserState(data.user);
                    return;
                }
            }
            await updateUserState(null);
        } catch (err) { await updateUserState(null); }
    };

    const updateUserState = async (user) => {
        state.user = user;
        if (user) {
            loginNavBtn.classList.add('hidden');
            const registerNavBtn = document.getElementById('register-nav-btn');
            if (registerNavBtn) registerNavBtn.classList.add('hidden');
            loggedInState.classList.remove('hidden');
            userNameDisplay.textContent = `Hi, ${(user.name || 'User').split(' ')[0]}`; // First name only in nav
            authModal.classList.add('hidden');
            
            const adminBtn = document.getElementById('admin-nav-btn');
            if (adminBtn) {
                if (user.email === 'admin@bookurticket.com') {
                    adminBtn.classList.remove('hidden');
                    // Completely hide user UI
                    const navCenter = document.querySelector('.nav-center');
                    if(navCenter) navCenter.classList.add('hidden');
                    document.querySelectorAll('.nav-link').forEach(l => {
                        if(l.id !== 'user-display-name') l.classList.add('hidden');
                    });
                    const hero = document.querySelector('.hero');
                    if(hero) hero.classList.add('hidden');
                    
                    document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
                    document.getElementById('admin-view').classList.remove('hidden');
                    renderAdminDashboard();
                } else {
                    adminBtn.classList.add('hidden');
                    const navCenter = document.querySelector('.nav-center');
                    if(navCenter) navCenter.classList.remove('hidden');
                    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('hidden'));
                    const hero = document.querySelector('.hero');
                    if(hero) hero.classList.remove('hidden');
                }
            }

            // Populate Profile Info
            document.getElementById('profile-name').textContent = user.name || 'User';
            document.getElementById('profile-email').textContent = user.email || '';
            
            const avatarImg = document.getElementById('profile-avatar-img');
            const avatarText = document.getElementById('profile-avatar-text');
            const deleteAvatarBtn = document.getElementById('delete-avatar-btn');

            if (user.avatar_url && avatarImg && avatarText) {
                avatarImg.src = user.avatar_url + "?t=" + new Date().getTime(); // Prevent caching issues
                avatarImg.style.display = 'block';
                avatarText.style.display = 'none';
                if(deleteAvatarBtn) deleteAvatarBtn.classList.remove('hidden');
            } else if (avatarImg && avatarText) {
                avatarImg.style.display = 'none';
                avatarText.style.display = 'block';
                avatarText.textContent = (user.name || 'U').charAt(0).toUpperCase();
                if(deleteAvatarBtn) deleteAvatarBtn.classList.add('hidden');
            }

            // Load Favorites
            try {
                const res = await fetch('/api/favorites');
                if (res.ok) {
                    const favs = await res.json();
                    state.favorites = favs.map(f => f.id);
                }
            } catch (e) {}

        } else {
            loginNavBtn.classList.remove('hidden');
            const registerNavBtn = document.getElementById('register-nav-btn');
            if (registerNavBtn) registerNavBtn.classList.remove('hidden');
            loggedInState.classList.add('hidden');
            state.favorites = [];
        }
        
        // Refresh grids to reflect heart status
        if(!document.getElementById('movies-view').classList.contains('hidden')) renderHome();
        if(!document.getElementById('cinemas-view').classList.contains('hidden')) renderCinemas();
        if(!document.getElementById('profile-view').classList.contains('hidden')) {
            renderDashboard();
            renderWishlist();
        }
    };

    window.toggleAuthModal = (show) => {
        authModal.classList.toggle('hidden', !show);
        if (show) window.toggleAuth('login');
    };

    window.toggleAuth = (type) => {
        document.getElementById('login-form').classList.toggle('hidden', type !== 'login');
        document.getElementById('register-form').classList.toggle('hidden', type !== 'register');
        const forgotForm = document.getElementById('forgot-password-form');
        if (forgotForm) forgotForm.classList.toggle('hidden', type !== 'forgot-password');
    };

    // --- GOOGLE LOGIN (HIGH-FIDELITY SIMULATION) ---
    window.handleGoogleLogin = () => {
        const modal = document.getElementById('google-chooser-modal');
        const list = document.getElementById('google-accounts-list');
        if(!modal || !list) return;

        // Populate with common test accounts or current user
        const knownAccounts = [
            { email: 'bakaleanju@gmail.com', name: 'Anjali Bakale' },
            { email: 'tester.movies@gmail.com', name: 'Test User' }
        ];

        list.innerHTML = knownAccounts.map(acc => `
            <div class="google-account-item" onclick="confirmGoogleAccount('${acc.email}', '${acc.name}')">
                <div class="google-avatar-circle">${acc.name.charAt(0)}</div>
                <div class="google-acc-info">
                    <div class="google-acc-name">${acc.name}</div>
                    <div class="google-acc-email">${acc.email}</div>
                </div>
            </div>
        `).join('') + `
            <div class="google-account-item" onclick="promptOtherGoogleAccount()">
                <div class="google-avatar-circle" style="background: #f1f3f4; color: #5f6368;">👤</div>
                <div class="google-acc-info">
                    <div class="google-acc-name" style="color: #1a73e8;">Use another account</div>
                </div>
            </div>
        `;

        modal.classList.remove('hidden');
    };

    window.promptOtherGoogleAccount = () => {
        const email = window.prompt("Enter your Google Email:");
        if (email && email.includes('@')) {
            confirmGoogleAccount(email.toLowerCase(), email.split('@')[0]);
        }
    };

    window.confirmGoogleAccount = async (email, name) => {
        const modal = document.getElementById('google-chooser-modal');
        const header = modal.querySelector('.google-chooser-header');
        const originalHeader = header.innerHTML;
        
        // Show realistic Material Spinner
        header.innerHTML = `
            <div style="display:flex; flex-direction:column; align-items:center; padding: 2rem 0;">
                <div class="google-spinner"></div>
                <p style="margin-top: 1.5rem; color: #5f6368; font-size: 0.9rem;">Verifying your account...</p>
            </div>
        `;
        
        try {
            const res = await fetch('/api/google-login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, name })
            });
            const data = await res.json();
            if (data.success) {
                setTimeout(() => {
                    updateUserState(data.user);
                    showToast(`Signed in as ${data.user.name} via Google`);
                    modal.classList.add('hidden');
                    header.innerHTML = originalHeader; // reset
                    toggleAuthModal(false);
                }, 1500); // Cinematic latency
            }
        } catch (err) { 
            showToast("Google connection failed", "error"); 
            header.innerHTML = originalHeader;
        }
    };

    // --- MOVIE RENDERING ---
    const fetchMovies = async () => {
        const res = await fetch('/api/movies');
        state.movies = await res.json();
        state.topMovies = state.movies.filter(m => m.is_top);
    };

    const renderHome = () => {
        topMoviesGrid.innerHTML = state.topMovies.map(movie => createMovieCard(movie)).join('');
    };

    const renderCinemas = () => {
        const groups = state.movies.reduce((acc, m) => {
            acc[m.language] = acc[m.language] || [];
            acc[m.language].push(m);
            return acc;
        }, {});

        languageSectionsContainer.innerHTML = Object.entries(groups).map(([lang, items]) => `
            <div class="lang-section">
                <h2 class="section-title" style="text-align: left; margin-bottom: 2rem;">${lang} Cinemas</h2>
                <div class="movies-grid">
                    ${items.map(m => createMovieCard(m)).join('')}
                </div>
            </div>
        `).join('');
    };

    window.formatTrailerUrl = (url) => {
        if (!url) return "";
        // Robust YouTube ID extraction regex
        const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
        const match = url.match(regExp);
        const id = (match && match[2].length === 11) ? match[2] : null;
        return id ? `https://www.youtube-nocookie.com/embed/${id}` : url;
    };

    const createMovieCard = (movie) => {
        const isFav = state.favorites.includes(movie.id);
        const rating = (4.0 + (movie.id % 10) / 10).toFixed(1);
        const trailerEmbed = formatTrailerUrl(movie.trailer_url);
        
        return `
        <div class="movie-card" style="position: relative;">
            <button class="fav-btn ${isFav ? 'active' : ''}" onclick="toggleFavorite(${movie.id}, this)">
                ${isFav ? '❤️' : '🤍'}
            </button>
            <div class="movie-img-wrapper open-booking-btn" style="position: relative; cursor: pointer;" data-id="${movie.id}">
                <img src="${movie.image_url}" alt="${movie.title}" style="pointer-events: none;">
                <button class="play-btn" data-url="${trailerEmbed}">▶</button>
            </div>
            <div class="movie-card-info">
                <h3>${movie.title}</h3>
                <p>⭐ ${rating}/5 | ${movie.genre} | ${movie.language}</p>
                <button class="btn btn-primary book-now-btn open-booking-btn" data-id="${movie.id}" style="width:100%; margin-top: 0.8rem; padding: 0.6rem 1rem; font-size: 0.9rem; border-radius: 8px;">🎟️ Book Tickets</button>
            </div>
        </div>
        `;
    };

    window.openTrailer = (url, event) => {
        event.stopPropagation();
        if(!url) return showToast("Trailer not available", "error");
        
        // Ensure accurate query parameter joining
        const connector = url.includes('?') ? '&' : '?';
        document.getElementById('trailer-iframe').src = url + connector + "autoplay=1&mute=1";
        document.getElementById('trailer-modal').classList.remove('hidden');
    };

    window.closeTrailer = () => {
        document.getElementById('trailer-iframe').src = "";
        document.getElementById('trailer-modal').classList.add('hidden');
    };

    window.toggleFavorite = async (movieId, btnElement) => {
        if (!state.user) return window.toggleAuthModal(true);

        const isFav = state.favorites.includes(movieId);
        const action = isFav ? 'remove' : 'add';

        // Optimistic UI Update
        if (isFav) state.favorites = state.favorites.filter(id => id !== movieId);
        else state.favorites.push(movieId);
        
        // Update all instances on the screen, but specifically handle the clicked one
        if (btnElement) {
            btnElement.classList.toggle('active', !isFav);
            btnElement.textContent = !isFav ? '❤️' : '🤍';
        }
        
        const buttons = document.querySelectorAll(`.fav-btn[onclick*="toggleFavorite(${movieId}"]`);
        buttons.forEach(btn => {
            if (btn !== btnElement) {
                btn.classList.toggle('active', !isFav);
                btn.textContent = !isFav ? '❤️' : '🤍';
            }
        });

        try {
            await fetch('/api/favorites', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ movie_id: movieId, action })
            });
            if(document.getElementById('profile-view').classList.contains('active')) renderWishlist();
        } catch (e) { showToast("Error updating wishlist", "error"); }
    };

    // --- BOOKING MODAL & STEPS ---
    window.openBookingModal = async (movieId) => {
        console.log("DEBUG: openBookingModal triggered for ID:", movieId);
        
        if (!state.user) {
            showToast("You must be logged in to book movie tickets.", "error");
            window.toggleAuthModal(true);
            return;
        }

        const modal = document.getElementById('booking-modal');
        if (!modal) {
            console.error("DEBUG: #booking-modal NOT FOUND!");
            return;
        }

        try {
            // Force visibility
            try {
                modal.classList.remove('hidden');
            } catch (e) {
                console.error("DEBUG: Error removing hidden class:", e);
            }
            modal.style.display = 'flex'; 
            switchStep(1);
            console.log("DEBUG: Modal classList after remove:", modal.className);
        } catch (e) {
            console.error("DEBUG: Error opening modal:", e);
        }

        const movie = state.movies.find(m => m.id == movieId);
        if (!movie) {
            console.warn("DEBUG: Movie not in cached state, attempting to fetch list...");
            await fetchMovies();
        }
        
        const targetMovie = state.movies.find(m => m.id == movieId);
        if(!targetMovie) {
            console.error("DEBUG: Movie STILL not found after refresh:", movieId);
            // Fallback: use whatever info we have if it's a search match
            return;
        }

        state.selectedMovie = targetMovie;
        state.selectedSeats.clear();
        state.selectedShowtime = null;
        state.seatTotal = 0;
        state.snacksTotal = 0;
        state.snacks = { popcorn: 0, coke: 0, nachos: 0 };
        
        try {
            document.getElementById('qty-popcorn').textContent = "0";
            document.getElementById('qty-coke').textContent = "0";
            document.getElementById('qty-nachos').textContent = "0";
            document.getElementById('fnb-btn-total').textContent = "0";

            document.getElementById('modal-movie-img').src = targetMovie.image_url;
            document.getElementById('modal-movie-title').textContent = targetMovie.title;
            document.getElementById('modal-movie-synopsis').textContent = targetMovie.synopsis;
            document.getElementById('modal-trailer-btn').onclick = (e) => {
                e.preventDefault();
                window.openTrailer(formatTrailerUrl(targetMovie.trailer_url), e);
            };
        } catch (e) { console.error("DEBUG: Error populating modal info:", e); }

        console.log("DEBUG: Fetching showtimes...");
        try {
            const res = await fetch(`/api/movies/${targetMovie.id}/showtimes`);
            const showtimes = await res.json();
            renderShowtimes(showtimes);
            console.log("DEBUG: Showtimes rendered.");
        } catch (err) {
            console.error("DEBUG: Error fetching showtimes:", err);
        }
    };

    const renderShowtimes = (showtimes) => {
        const list = document.getElementById('showtimes-list');
        list.innerHTML = showtimes.map(st => `
            <button class="btn btn-outline" onclick="selectShowtime(${st.id}, '${st.time}')">${st.time}</button>
        `).join('');
    };

    window.selectShowtime = async (id, time) => {
        state.selectedShowtime = { id, time };
        // Fetch Seats
        const res = await fetch(`/api/showtimes/${id}/seats`);
        const data = await res.json();
        renderSeats(data.booked);
        switchStep(2);
    };

    const renderSeats = (booked) => {
        const map = document.getElementById('seats-map');
        map.innerHTML = '';
        const rows = ['A', 'B', 'C', 'D', 'E', 'F'];
        
        // Randomly simulate a busy theater if no seats booked from DB
        const simBusy = booked.length === 0;

        rows.forEach((row, rowIdx) => {
            const label = document.createElement('div');
            label.className = 'row-label';
            label.textContent = row;
            map.appendChild(label);
            
            for (let s = 1; s <= 10; s++) {
                const seatId = `${row}${s}`;
                let isBooked = booked.includes(seatId);
                
                // Add Simulator logic for realism
                if (simBusy && !isBooked && Math.random() > 0.8) isBooked = true;

                let tier = 'classic';
                let price = 250;
                if (rowIdx >= 2 && rowIdx <= 4) { tier = 'prime'; price = 350; }
                if (rowIdx === 5) { tier = 'recliner'; price = 500; }

                const seatDiv = document.createElement('div');
                seatDiv.className = `seat ${tier} ${isBooked ? 'occupied' : 'available'}`;
                seatDiv.textContent = s;
                seatDiv.dataset.price = price;
                
                seatDiv.onclick = () => !isBooked && toggleSeat(seatId, seatDiv, price);
                map.appendChild(seatDiv);
            }
        });
    };

    const toggleSeat = (id, el, price) => {
        if (state.selectedSeats.has(id)) {
            state.selectedSeats.delete(id);
            el.classList.remove('selected');
            state.seatTotal -= price;
        } else {
            state.selectedSeats.add(id);
            el.classList.add('selected');
            state.seatTotal += price;
        }
        document.getElementById('confirm-seats-btn').disabled = state.selectedSeats.size === 0;
    };

    const switchStep = (step) => {
        state.currentStep = step;
        document.querySelectorAll('.booking-step').forEach(s => s.classList.add('hidden'));
        document.getElementById(`step-${step}`).classList.remove('hidden');
    };

    // --- F&B SNACK BAR & PAYMENT ---
    document.getElementById('confirm-seats-btn').onclick = () => {
        // Now moves to Snack Bar (Step 3)
        switchStep(3);
    };

    window.updateFnb = (item, amt) => {
        const prices = { popcorn: 250, coke: 150, nachos: 300 };
        state.snacks[item] = Math.max(0, state.snacks[item] + amt);
        document.getElementById(`qty-${item}`).textContent = state.snacks[item];
        
        state.snacksTotal = (state.snacks.popcorn * prices.popcorn) + 
                            (state.snacks.coke * prices.coke) + 
                            (state.snacks.nachos * prices.nachos);
                            
        document.getElementById('fnb-btn-total').textContent = state.snacksTotal;
    };

    document.getElementById('confirm-fnb-btn').onclick = () => {
        if (!state.user) {
            showToast("Quick! Sign in to secure your seats and complete the booking.", "error");
            window.toggleAuthModal(true);
            return;
        }
        const grandTotal = state.seatTotal + state.snacksTotal;
        document.getElementById('total-price').textContent = grandTotal;
        
        // Setup UPI Component dynamically (with safe guards for cached HTML)
        const upiAmtDisplay = document.getElementById('upi-amount-display');
        if (upiAmtDisplay) {
            upiAmtDisplay.textContent = grandTotal;
            // The user has hardcoded their own QR code, so do not override the image!
            // const upiUri = `upi://pay?pa=bookurticket@icici&pn=BookUrTicket&am=${grandTotal}.00&cu=INR`;
            // const qrImg = document.getElementById('upi-qr-img');
            // if(qrImg) qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(upiUri)}`;
        }
        
        if (typeof window.setPaymentMethod === 'function') window.setPaymentMethod(null);
        
        switchStep(4); // Move to Payment
    };

    window.setPaymentMethod = (method) => {
        window.currentPaymentMethod = method;
        
        // Hide both containers and Reset tabs
        document.getElementById('tab-card').classList.replace('btn-primary', 'btn-outline');
        document.getElementById('tab-upi').classList.replace('btn-primary', 'btn-outline');
        document.getElementById('payment-card-container').classList.add('hidden');
        if(document.getElementById('payment-upi-container')) document.getElementById('payment-upi-container').classList.add('hidden');
        document.getElementById('pay-now-btn').classList.add('hidden');

        if(method === 'card') {
            document.getElementById('tab-card').classList.replace('btn-outline', 'btn-primary');
            document.getElementById('payment-card-container').classList.remove('hidden');
            document.getElementById('pay-now-btn').classList.remove('hidden');
        } else if(method === 'upi') {
            document.getElementById('tab-upi').classList.replace('btn-outline', 'btn-primary');
            if(document.getElementById('payment-upi-container')) document.getElementById('payment-upi-container').classList.remove('hidden');
            document.getElementById('pay-now-btn').classList.remove('hidden');
        }
    };
    window.currentPaymentMethod = null;

    // Card Input Masking Visual
    const cardInput = document.getElementById('card-input');
    if(cardInput) {
        cardInput.oninput = e => {
            let val = e.target.value.replace(/\D/g, '').substring(0, 16);
            val = val.match(/.{1,4}/g)?.join(' ') || val;
            e.target.value = val;
            document.getElementById('card-number-display').textContent = val || "0000 0000 0000 0000";
        };
    }

    const cardNameInput = document.getElementById('card-name-input');
    if(cardNameInput) {
        cardNameInput.oninput = e => {
            document.getElementById('card-name-display').textContent = e.target.value.toUpperCase() || "YOUR NAME";
        };
    }

    const expiryInput = document.getElementById('expiry-input');
    if(expiryInput) {
        expiryInput.oninput = e => {
            let val = e.target.value.replace(/\D/g, '').substring(0, 4);
            if (val.length > 2) val = val.substring(0, 2) + '/' + val.substring(2);
            e.target.value = val;
        };
    }

    const cvvInput = document.getElementById('cvv-input');
    if(cvvInput) {
        cvvInput.oninput = e => {
            e.target.value = e.target.value.replace(/\D/g, '').substring(0, 3);
        };
    }

    document.getElementById('pay-now-btn').onclick = async () => {
        if (window.currentPaymentMethod === 'upi') {
            const upiRef = document.getElementById('upi-ref-input').value.trim();
            if (upiRef.length !== 12 || isNaN(upiRef)) {
                showToast("Please enter a valid 12-digit UPI Reference / UTR Number", "error");
                return;
            }
        } else {
            const cardVal = document.getElementById('card-input').value.replace(/\s/g, '');
            const cardName = document.getElementById('card-name-input').value.trim();
            const expiry = document.getElementById('expiry-input').value.trim();
            const cvv = document.getElementById('cvv-input').value.trim();

            if (!cardName || cardVal.length < 12 || expiry.length < 5 || cvv.length < 3) {
                showToast("All payment fields are required and must be valid", "error");
                return;
            }
        }

        const payload = {
            showtime_id: state.selectedShowtime.id,
            seats: Array.from(state.selectedSeats),
            user_email: state.user.email,
            movie_title: state.selectedMovie.title,
            time: state.selectedShowtime.time,
            amount: state.seatTotal + state.snacksTotal
        };

        const res = await fetch('/api/bookings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            const data = await res.json();
            state.lastBookingId = data.booking_id;
            showToast("Payment Successful! E-Ticket sent to your Inbox 📥");
            generateTicket();
            switchStep(5);

        } else {
            showToast("Booking failed. Try again.", "error");
        }
    };

    const generateTicket = () => {
        const bgImg = document.getElementById('ticket-bg-img');
        if (bgImg) bgImg.src = state.selectedMovie.image_url;
        document.getElementById('ticket-movie').textContent = state.selectedMovie.title.toUpperCase();
        document.getElementById('ticket-time-text').textContent = state.selectedShowtime.time;
        document.getElementById('ticket-seats-text').textContent = Array.from(state.selectedSeats).join(', ');
        document.getElementById('ticket-total-text').textContent = `₹${state.seatTotal + state.snacksTotal}.00`;
        document.getElementById('ticket-date-text').textContent = new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).toUpperCase();
        
        if (state.user) {
            document.getElementById('ticket-user-name').textContent = state.user.name;
            document.getElementById('ticket-user-email').textContent = state.user.email;
        }
    };

    // Centralized Download Logic
    window.downloadTicketPDF = () => {
        if (!state.lastBookingId) {
            showToast("Error locating ticket document. Please check your email.", "error");
            return;
        }
        window.location.href = `/api/download-ticket/${state.lastBookingId}`;
    };
    // --- NAVIGATION ---
    const setupNav = () => {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.onclick = (e) => {
                e.preventDefault();
                const target = link.dataset.target;
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                
                document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
                document.getElementById(target).classList.remove('hidden');

                if (target === 'cinemas-view') renderCinemas();
                if (target === 'profile-view') {
                    renderDashboard();
                    renderWishlist();
                }
            };
        });

        const adminNavBtn = document.getElementById('admin-nav-btn');
        if (adminNavBtn) {
            adminNavBtn.onclick = (e) => {
                e.preventDefault();
                document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                document.getElementById('admin-view').classList.remove('hidden');
                renderAdminDashboard();
            };
        }

        const avatarUpload = document.getElementById('avatar-upload');
        if(avatarUpload) {
            avatarUpload.onchange = async (e) => {
                const file = e.target.files[0];
                if (!file) return;
                
                const formData = new FormData();
                formData.append('avatar', file);
                
                showToast("Uploading avatar...");
                try {
                    const res = await fetch('/api/upload-avatar', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();
                    if(data.success) {
                        state.user.avatar_url = data.avatar_url;
                        updateUserState(state.user); // refresh UI
                        showToast("Avatar updated successfully!");
                    } else {
                        showToast(data.error || "Upload failed", "error");
                    }
                } catch(err) {
                    showToast("Error connecting to server", "error");
                }
            };
        }

        const deleteAvatarBtn = document.getElementById('delete-avatar-btn');
        if(deleteAvatarBtn) {
            deleteAvatarBtn.onclick = async () => {
                if(!confirm("Are you sure you want to remove your profile picture?")) return;
                
                showToast("Removing avatar...");
                try {
                    const res = await fetch('/api/delete-avatar', { method: 'POST' });
                    const data = await res.json();
                    if(data.success) {
                        state.user.avatar_url = null;
                        updateUserState(state.user);
                        showToast("Avatar removed successfully!");
                    } else {
                        showToast(data.error || "Failed to remove avatar", "error");
                    }
                } catch (err) {
                    showToast("Server error", "error");
                }
            };
        }

        document.getElementById('update-password-btn').onclick = async () => {
            const newPassword = document.getElementById('new-password-input').value;
            if(!newPassword) return showToast("Enter a new password", "error");
            
            const btn = document.getElementById('update-password-btn');
            btn.textContent = "Updating...";
            try {
                const res = await fetch('/api/change-password', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({new_password: newPassword})
                });
                if(res.ok) {
                    showToast("Password updated successfully! 🔒");
                    document.getElementById('new-password-input').value = "";
                } else {
                    showToast("Failed to update password", "error");
                }
            } catch(e) { showToast("Error connecting to server", "error"); }
            btn.textContent = "Update Securely";
        };

        loginNavBtn.onclick = () => window.toggleAuthModal(true);
        const registerNavBtn = document.getElementById('register-nav-btn');
        if (registerNavBtn) {
            registerNavBtn.onclick = () => {
                window.toggleAuthModal(true);
                window.toggleAuth('register');
            };
        }
        document.getElementById('to-register').onclick = () => window.toggleAuth('register');
        document.getElementById('to-login').onclick = () => window.toggleAuth('login');
        
        // Submission logic
        const performLogin = async () => {
            let email = document.getElementById('login-email').value.trim().toLowerCase();
            const password = document.getElementById('login-password').value;
            if (!email || !password) return showToast("All fields required", "error");
            
            try {
                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                
                if (!res.ok) {
                    const errorData = await res.json().catch(() => ({ error: "Invalid credentials or Server Error" }));
                    return showToast(errorData.error || "Login Failed", "error");
                }

                const data = await res.json();
                if (data.success) {
                    // Navigate to home view before updating state so the UI refresh catches it
                    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                    const homeLink = document.querySelector('[data-target="movies-view"]');
                    if (homeLink) homeLink.classList.add('active');
                    
                    document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
                    document.getElementById('movies-view').classList.remove('hidden');
                    
                    // Clear inputs
                    document.getElementById('login-email').value = '';
                    document.getElementById('login-password').value = '';
                    
                    await updateUserState(data.user);
                    showToast(`Welcome back, ${data.user.name}!`);
                }
            } catch (err) { 
                console.error("Login Error:", err);
                showToast("Server connection error", "error"); 
            }
        };

        const performRegister = async () => {
            const name = document.getElementById('reg-name').value.trim();
            const email = document.getElementById('reg-email').value.trim().toLowerCase();
            const password = document.getElementById('reg-password').value;
            if (!name || !email || !password) return showToast("All fields required", "error");

            try {
                const res = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, password })
                });
                const data = await res.json();
                if (data.success) {
                    showToast("Registration successful! Please login.");
                    document.getElementById('login-email').value = email;
                    document.getElementById('login-password').value = '';
                    window.toggleAuth('login');
                    document.getElementById('login-password').focus();
                } else showToast(data.error, "error");
            } catch (err) { showToast("Server error", "error"); }
        };

        document.getElementById('login-submit').onclick = performLogin;
        document.getElementById('reg-submit').onclick = performRegister;

        // Add Enter Key Support
        document.getElementById('login-email').onkeydown = (e) => { if(e.key === 'Enter') performLogin(); };
        document.getElementById('login-password').onkeydown = (e) => { if(e.key === 'Enter') performLogin(); };
        document.getElementById('reg-name').onkeydown = (e) => { if(e.key === 'Enter') performRegister(); };
        document.getElementById('reg-email').onkeydown = (e) => { if(e.key === 'Enter') performRegister(); };
        document.getElementById('reg-password').onkeydown = (e) => { if(e.key === 'Enter') performRegister(); };

        logoutBtn.onclick = async () => {
            await fetch('/api/logout', { method: 'POST' });
            updateUserState(null);
            showToast("Logged out successfully");
            location.reload();
        };
    };

    const renderDashboard = async () => {
        if (!state.user) return;
        const res = await fetch('/api/my-bookings');
        const data = await res.json();
        dashboardTickets.innerHTML = data.map(b => `
            <div class="movie-card">
                <div class="movie-img-wrapper">
                    <img src="${b.image_url}" alt="${b.title}">
                </div>
                <div class="movie-card-info" style="padding: 1rem;">
                    <h3 style="font-size: 1rem;">${b.title}</h3>
                    <p style="font-size: 0.8rem; color: #888; margin-bottom: 0.5rem;">${b.time} | Seats: ${b.seats}</p>
                    <button class="btn btn-outline w-full" style="padding: 0.5rem;" onclick="window.showPastTicket('${b.title}', '${b.time}', '${b.seats}', '${b.amount}')">🎟️ View & Download</button>
                </div>
            </div>
        `).join('');
    };

    window.showPastTicket = (title, time, seats, amount) => {
        // Re-generate the fantastic ticket view
        const movie = state.movies.find(m => m.title === title);
        if(movie) document.getElementById('ticket-bg-img').src = movie.image_url;
        
        document.getElementById('ticket-movie').textContent = title.toUpperCase();
        document.getElementById('ticket-time-text').textContent = time;
        document.getElementById('ticket-seats-text').textContent = seats;
        const totalAmount = parseFloat(amount);
        document.getElementById('ticket-total-text').textContent = isNaN(totalAmount) ? `₹---` : `₹${totalAmount.toFixed(2)}`;
        document.getElementById('ticket-date-text').textContent = "PAST SHOW";
        
        if (state.user) {
            document.getElementById('ticket-user-name').textContent = state.user.name;
            document.getElementById('ticket-user-email').textContent = state.user.email;
        }
        
        switchStep(5);
        bookingModal.classList.remove('hidden');
    };

    const renderWishlist = async () => {
        if (!state.user) return;
        const res = await fetch('/api/favorites');
        const data = await res.json();
        const grid = document.getElementById('wishlist-grid');
        
        if (data.length === 0) {
            grid.innerHTML = `<p style="grid-column: 1/-1; text-align: center; color: #888; font-size: 1.2rem;">Your wishlist is empty. Tap the 🤍 on any movie to add it here!</p>`;
        } else {
            grid.innerHTML = data.map(m => createMovieCard(m)).join('');
        }
    };

    window.shareTicket = () => {
        if(!state.selectedMovie) return;
        const text = `I just booked tickets for *${state.selectedMovie.title}* via BookUrTicket! 🎟️🍿\nSeats: ${Array.from(state.selectedSeats).join(', ')}`;
        window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`, '_blank');
    };

    // --- SEARCH & FILTERS ---
    const setupSearch = () => {
        // Setup Filter Chips
        const chipsContainer = document.getElementById('filter-chips-container');
        const filters = ['All', 'Action', 'Drama', 'Comedy', 'Hindi', 'Telugu'];
        if(chipsContainer) {
            chipsContainer.innerHTML = filters.map(f => 
                `<button class="chip ${f==='All'?'active':''}" onclick="applyFilter('${f}', event)">${f}</button>`
            ).join('');
        }

        window.applyFilter = (filter, event) => {
            document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
            event.target.classList.add('active');
            
            const grid = document.getElementById('top-movies-grid');
            let filtered = state.movies;
            if (filter !== 'All') {
                filtered = state.movies.filter(m => m.genre.includes(filter) || m.language === filter);
            }
            grid.innerHTML = filtered.map(m => createMovieCard(m)).join('');
        };
        globalSearch.oninput = (e) => {
            const query = e.target.value.toLowerCase();
            if (query.length < 2) { 
                searchResults.classList.add('hidden'); 
                return; 
            }
            
            const matches = state.movies.filter(m => 
                m.title.toLowerCase().includes(query) || 
                m.genre.toLowerCase().includes(query) || 
                m.language.toLowerCase().includes(query)
            );

            if (matches.length > 0) {
                searchResults.innerHTML = matches.map(m => `
                    <div class="search-result-item" onclick="openBookingModal('${m.id}')">
                        <img src="${m.image_url}" alt="${m.title}">
                        <div class="search-result-info">
                            <h4>${m.title}</h4>
                            <p>${m.language} | ${m.genre}</p>
                        </div>
                        <button class="btn btn-minimal" onclick="window.openTrailer('${formatTrailerUrl(m.trailer_url)}', event)" 
                                style="margin-left: auto; font-size: 1.2rem; min-width: 40px;">▶️</button>
                    </div>
                `).join('');
            } else {
                searchResults.innerHTML = `
                    <div style="padding: 2rem; text-align: center; color: #888;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔍</div>
                        <div style="font-weight: 600;">No results found for "${e.target.value}"</div>
                        <div style="font-size: 0.85rem; opacity: 0.7;">Try searching for a different movie, genre, or language.</div>
                    </div>
                `;
            }
            searchResults.classList.remove('hidden');
        };
    };

    // --- UTILS ---
    const showToast = (msg, type = "success") => {
        const t = document.createElement('div');
        t.className = `toast ${type}`;
        t.textContent = msg;
        document.getElementById('toast-container').appendChild(t);
        setTimeout(() => t.remove(), 4000);
    };

    // --- MODAL CLICK OUTSIDE ---
    window.onclick = e => {
        if (e.target == authModal) authModal.classList.add('hidden');
        if (e.target == bookingModal) bookingModal.classList.add('hidden');
    };

    closeModal.onclick = () => bookingModal.classList.add('hidden');
    document.querySelectorAll('[data-target]').forEach(b => {
        b.onclick = (e) => { if(e.target.dataset.target) switchStep(parseInt(e.target.dataset.target)) };
    });

    // --- ADMIN LOGIC ---
    const renderAdminDashboard = async () => {
        if (!state.user || state.user.email !== 'admin@bookurticket.com') return;

        try {
            const metricsRes = await fetch('/api/admin/metrics');
            const metrics = await metricsRes.json();
            document.getElementById('admin-users-count').textContent = metrics.users;
            document.getElementById('admin-revenue-count').textContent = `₹${metrics.revenue}`;
            document.getElementById('admin-bookings-count').textContent = metrics.bookings;
        } catch(e) {}

        try {
            const listRes = await fetch('/api/admin/bookings');
            const bookingsList = await listRes.json();
            document.getElementById('admin-bookings-list').innerHTML = bookingsList.map(b => `
                <tr>
                    <td>#${b.id}</td>
                    <td>${b.user_name || b.user_email}</td>
                    <td><strong>${b.title}</strong></td>
                    <td>${b.time}</td>
                    <td>${b.seats}</td>
                    <td style="position: sticky; right: 0; background: white; box-shadow: -2px 0 5px rgba(0,0,0,0.05);"><button class="btn btn-minimal delete-booking-btn" style="color: #ff3366; padding: 5px; font-weight: bold;" data-id="${b.id}">🗑️ Delete</button></td>
                </tr>
            `).join('');
        } catch(e) {}

        try {
            const usersRes = await fetch('/api/admin/users');
            const usersList = await usersRes.json();
            document.getElementById('admin-users-list').innerHTML = usersList.map(u => `
                <tr>
                    <td>#${u.id}</td>
                    <td><strong>${u.name}</strong></td>
                    <td>${u.email}</td>
                </tr>
            `).join('');
        } catch(e) {}

        try {
            const moviesRes = await fetch('/api/movies');
            const moviesList = await moviesRes.json();
            document.getElementById('admin-movies-list').innerHTML = moviesList.map(m => `
                <tr>
                    <td><img src="${m.image_url}" style="width:40px; height:50px; object-fit:cover; border-radius:4px;"></td>
                    <td>#${m.id}</td>
                    <td><strong>${m.title}</strong></td>
                    <td>${m.language}</td>
                    <td>${m.genre}</td>
                    <td>${m.is_top ? '⭐ Yes' : 'No'}</td>
                    <td><button class="btn btn-minimal view-trailer-btn" data-url="${formatTrailerUrl(m.trailer_url)}">📺 View</button></td>
                    <td style="position: sticky; right: 0; background: white; box-shadow: -2px 0 5px rgba(0,0,0,0.05);"><button class="btn btn-minimal delete-movie-btn" style="color: #ff3366; padding: 5px; font-weight: bold;" data-id="${m.id}">🗑️ Delete</button></td>
                </tr>
            `).join('');
        } catch(e) {}
    };

    window.deleteBooking = async (id) => {
        if (!confirm(`Are you sure you want to delete purchase #${id}? This action cannot be undone.`)) return;
        try {
            const res = await fetch(`/api/admin/bookings/${id}`, { method: 'DELETE' });
            if (res.ok) {
                showToast("Transaction deleted and removed from history.");
                renderAdminDashboard();
            }
        } catch (e) { showToast("Failed to delete booking", "error"); }
    };

    window.deleteMovie = async (id) => {
        if (!confirm(`CAUTION: Are you sure you want to delete movie #${id}? All associated showtimes will also be removed.`)) return;
        try {
            const res = await fetch(`/api/admin/movies/${id}`, { method: 'DELETE' });
            if (res.ok) {
                showToast("Movie removed from system.");
                await fetchMovies(); // Refresh main state
                renderAdminDashboard(); // Refresh dash
            }
        } catch (e) { showToast("Failed to delete movie", "error"); }
    };

    // --- SETUP ADMIN MOVIE ADDITION ---
    const setupAdminMovieAdd = () => {
        const addMovieBtn = document.getElementById('admin-add-movie-btn');
        if (!addMovieBtn) return;

        addMovieBtn.onclick = async () => {
            const payload = {
                title: document.getElementById('admin-movie-title').value.trim(),
                synopsis: document.getElementById('admin-movie-synopsis').value.trim(),
                genre: document.getElementById('admin-movie-genre').value.trim(),
                language: document.getElementById('admin-movie-lang').value,
                image_url: document.getElementById('admin-movie-img').value.trim(),
                trailer_url: document.getElementById('admin-movie-trailer').value.trim(),
                is_top: document.getElementById('admin-is-top').checked
            };

            if (!payload.title || !payload.synopsis || !payload.image_url || !payload.genre) {
                return showToast("Please fill in all core movie details!", "error");
            }

            addMovieBtn.disabled = true;
            addMovieBtn.innerHTML = `<span>Uploading... ⚙️</span>`;

            try {
                const res = await fetch('/api/admin/movies', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                const data = await res.json();
                if (data.success) {
                    showToast("Movie added to inventory successfully! 🎬");
                    // Reset fields
                    ['admin-movie-title', 'admin-movie-synopsis', 'admin-movie-genre', 'admin-movie-img', 'admin-movie-trailer'].forEach(id => {
                        document.getElementById(id).value = "";
                    });
                    document.getElementById('admin-is-top').checked = false;
                    
                    // Refresh movies and the admin dashboard table immediately
                    await fetchMovies();
                    renderAdminDashboard();
                    renderHome(); 
                    renderCinemas();
                } else {
                    showToast(data.error || "Failed to add movie", "error");
                }
            } catch (err) {
                showToast("Connection error to admin API", "error");
            } finally {
                addMovieBtn.disabled = false;
                addMovieBtn.textContent = "🚀 Upload Movie to Portal";
            }
        };
    };
    document.getElementById('admin-movies-list').addEventListener('click', function(e) {
        const deleteBtn = e.target.closest('.delete-movie-btn');
        if (deleteBtn) {
            const id = deleteBtn.dataset.id;
            window.deleteMovie(id);
            return;
        }

        const trailerBtn = e.target.closest('.view-trailer-btn');
        if (trailerBtn) {
            const url = trailerBtn.dataset.url;
            window.openTrailer(url, e);
            return;
        }
    });

    document.getElementById('admin-bookings-list').addEventListener('click', function(e) {
        const deleteBookingBtn = e.target.closest('.delete-booking-btn');
        if (deleteBookingBtn) {
            const id = deleteBookingBtn.dataset.id;
            window.deleteBooking(id);
        }
    });

    // Global event delegation for movie cards
    document.body.addEventListener('click', function(e) {

        const playBtn = e.target.closest('.play-btn');
        if (playBtn) {
            e.stopPropagation();
            const url = playBtn.dataset.url;
            window.openTrailer(url, e);
            return;
        }

        const bookingBtn = e.target.closest('.open-booking-btn');
        if (bookingBtn) {
            const id = bookingBtn.dataset.id;
            window.openBookingModal(id);
            return;
        }
    });

    // Forgot Password Logic
    const forgotSubmit = document.getElementById('forgot-submit');
    if (forgotSubmit) {
        forgotSubmit.addEventListener('click', async () => {
            const email = document.getElementById('forgot-email').value.trim();
            if (!email) return showToast("Please enter your registered email address.", "error");
            
            forgotSubmit.textContent = "Sending...";
            forgotSubmit.disabled = true;

            try {
                const res = await fetch('/api/forgot-password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email })
                });
                
                const data = await res.json();
                if (res.ok) {
                    showToast(data.message || "Temporary password sent to your email!", "success");
                    window.toggleAuth('login');
                } else {
                    showToast(data.error || "Failed to reset password", "error");
                }
            } catch (e) {
                showToast("Network error", "error");
            } finally {
                forgotSubmit.textContent = "Send Temporary Password";
                forgotSubmit.disabled = false;
            }
        });
    }

    init();
});
