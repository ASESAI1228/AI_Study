document.addEventListener('DOMContentLoaded', function() {
    // FAQ accordion functionality
    const faqItems = document.querySelectorAll('.faq-item');
    
    if (faqItems.length > 0) {
        faqItems.forEach(item => {
            const question = item.querySelector('.faq-question');
            const answer = item.querySelector('.faq-answer');
            const icon = item.querySelector('.faq-toggle i');
            
            // Initially hide all answers
            answer.style.display = 'none';
            
            question.addEventListener('click', () => {
                // Toggle the answer visibility
                if (answer.style.display === 'none') {
                    answer.style.display = 'block';
                    icon.classList.remove('fa-plus');
                    icon.classList.add('fa-minus');
                } else {
                    answer.style.display = 'none';
                    icon.classList.remove('fa-minus');
                    icon.classList.add('fa-plus');
                }
            });
        });
    }
    
    // Form validation
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Simple validation
            let isValid = true;
            const requiredFields = contactForm.querySelectorAll('[required]');
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });
            
            // Email validation
            const emailField = document.getElementById('email');
            if (emailField && emailField.value) {
                const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailPattern.test(emailField.value)) {
                    isValid = false;
                    emailField.classList.add('error');
                }
            }
            
            if (isValid) {
                // In a real application, this would submit the form data to a server
                alert('お問い合わせありがとうございます。担当者より折り返しご連絡いたします。');
                contactForm.reset();
            } else {
                alert('必須項目をすべて入力してください。');
            }
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Responsive navigation menu
    const menuToggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('nav ul');
    
    if (menuToggle && nav) {
        menuToggle.addEventListener('click', () => {
            nav.classList.toggle('active');
            menuToggle.classList.toggle('active');
        });
    }
    
    // Add active class to current page in navigation
    const currentPage = window.location.pathname.split('/').pop();
    const navLinks = document.querySelectorAll('nav ul li a');
    
    navLinks.forEach(link => {
        const linkPage = link.getAttribute('href');
        if (linkPage === currentPage || (currentPage === '' && linkPage === 'index.html')) {
            link.classList.add('active');
        }
    });
    
    // Testimonial slider (if exists)
    const testimonialSlider = document.querySelector('.testimonial-slider');
    if (testimonialSlider) {
        const testimonials = testimonialSlider.querySelectorAll('.testimonial');
        let currentSlide = 0;
        
        // Hide all testimonials except the first one
        testimonials.forEach((testimonial, index) => {
            if (index !== 0) {
                testimonial.style.display = 'none';
            }
        });
        
        // Auto-rotate testimonials
        setInterval(() => {
            testimonials[currentSlide].style.display = 'none';
            currentSlide = (currentSlide + 1) % testimonials.length;
            testimonials[currentSlide].style.display = 'block';
        }, 5000);
    }
    
    // Ensure video autoplay works across browsers
    const videos = document.querySelectorAll('video[autoplay]');
    videos.forEach(video => {
        // Force play the video immediately when DOM is loaded
        const playVideo = () => {
            // Set muted attribute to ensure autoplay works in most browsers
            video.muted = true;
            video.setAttribute('autoplay', '');
            video.setAttribute('playsinline', '');
            
            // Force play and handle any errors silently
            video.play().catch(error => {
                console.log('Autoplay prevented by browser policy. Will retry automatically.');
            });
        };
        
        // Try multiple approaches to ensure autoplay works
        
        // 1. Try to play video immediately
        playVideo();
        
        // 2. Try again when document is fully loaded
        if (document.readyState === 'complete') {
            playVideo();
        } else {
            window.addEventListener('load', playVideo);
        }
        
        // 3. Try again after a short delay (some browsers need this)
        setTimeout(playVideo, 500);
        
        // 4. Try again after a longer delay (for slower connections)
        setTimeout(playVideo, 2000);
        
        // 5. Try again on user interaction (this helps with strict browser policies)
        document.addEventListener('click', () => playVideo(), { once: true });
        document.addEventListener('touchstart', () => playVideo(), { once: true });
        
        // 6. Ensure video loops properly
        video.addEventListener('ended', () => {
            video.currentTime = 0;
            video.play().catch(e => console.log('Loop playback prevented'));
        });
    });
});
