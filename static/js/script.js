document.addEventListener('DOMContentLoaded', function() {
    initializeAnimations();
    initializeFormValidation();
    initializeSkillTags();
    initializeParallax();
    initializeLiveCounters();
    initializeScheduling();
});

function initializeScheduling() {
    // Set minimum date to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const minDate = tomorrow.toISOString().split('T')[0];
    
    const dateInput = document.getElementById('sessionDate');
    if (dateInput) {
        dateInput.setAttribute('min', minDate);
    }

    // Handle schedule button clicks
    document.querySelectorAll('.schedule-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const sessionId = this.dataset.sessionId;
            const partner = this.dataset.partner;
            const skill = this.dataset.skill;
            const role = this.dataset.role;

            // Populate modal with session info
            document.getElementById('modal-partner').textContent = partner;
            document.getElementById('modal-skill').textContent = skill;
            document.getElementById('modal-role').textContent = role;

            // Show the modal
            const modal = new bootstrap.Modal(document.getElementById('scheduleModal'));
            modal.show();
        });
    });

    // Handle schedule confirmation
    document.getElementById('confirmSchedule').addEventListener('click', function() {
        const form = document.getElementById('scheduleForm');
        
        if (!validateScheduleForm()) {
            return;
        }

        // Show loading state
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scheduling...';
        this.disabled = true;

        // Simulate API call
        setTimeout(() => {
            // Reset button
            this.innerHTML = '<i class="fas fa-paper-plane"></i> Schedule Session';
            this.disabled = false;

            // Hide schedule modal
            bootstrap.Modal.getInstance(document.getElementById('scheduleModal')).hide();

            // Show success modal
            showSuccessModal();

            // Reset form
            form.reset();
        }, 2000);
    });
}

function validateScheduleForm() {
    const date = document.getElementById('sessionDate').value;
    const time = document.getElementById('sessionTime').value;
    
    if (!date) {
        showAlert('Please select a date for your session.', 'warning');
        return false;
    }
    
    if (!time) {
        showAlert('Please select a time slot for your session.', 'warning');
        return false;
    }

    // Check if date is at least 24 hours from now
    const selectedDate = new Date(date + ' ' + time);
    const minDateTime = new Date();
    minDateTime.setHours(minDateTime.getHours() + 24);
    
    if (selectedDate < minDateTime) {
        showAlert('Please select a date and time at least 24 hours from now.', 'warning');
        return false;
    }

    return true;
}

function showSuccessModal() {
    const date = document.getElementById('sessionDate').value;
    const time = document.getElementById('sessionTime').value;
    const platform = document.querySelector('input[name="platform"]:checked').value;

    // Format date
    const dateObj = new Date(date);
    const formattedDate = dateObj.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    // Format time
    const timeObj = new Date('2000-01-01 ' + time);
    const formattedTime = timeObj.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });

    // Format platform
    const platformNames = {
        'zoom': 'Zoom',
        'google-meet': 'Google Meet',
        'teams': 'Microsoft Teams'
    };

    // Update success modal content
    document.getElementById('success-date').textContent = formattedDate;
    document.getElementById('success-time').textContent = formattedTime;
    document.getElementById('success-platform').textContent = platformNames[platform];

    // Show success modal
    const successModal = new bootstrap.Modal(document.getElementById('successModal'));
    successModal.show();

    // Add confetti effect
    createConfetti();
}

function createConfetti() {
    // Simple confetti effect
    const confettiContainer = document.createElement('div');
    confettiContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 9999;
    `;
    document.body.appendChild(confettiContainer);

    // Create confetti pieces
    for (let i = 0; i < 50; i++) {
        const confetti = document.createElement('div');
        confetti.style.cssText = `
            position: absolute;
            width: 10px;
            height: 10px;
            background: ${getRandomColor()};
            top: -10px;
            left: ${Math.random() * 100}%;
            animation: confettiFall ${2 + Math.random() * 3}s linear forwards;
        `;
        confettiContainer.appendChild(confetti);
    }

    // Remove confetti after animation
    setTimeout(() => {
        document.body.removeChild(confettiContainer);
    }, 5000);
}

function getRandomColor() {
    const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#f0932b', '#eb4d4b', '#6c5ce7'];
    return colors[Math.floor(Math.random() * colors.length)];
}

function initializeLiveCounters() {
  const userCountElement = document.getElementById('userCount');
  if (!userCountElement) return;

  const courseCountElement = document.getElementById('courseCount');
  if (courseCountElement) {
    courseCountElement.textContent = '50+';
  }

  const fetchAndAnimateUsers = async () => {
    try {
      const response = await fetch('/api/live-users');
      if (!response.ok) throw new Error('Failed to fetch live users');
      const data = await response.json();
      const liveUsers = data.live_users;
      const currentCount = parseInt(userCountElement.textContent.replace(/,/g, '')) || 0;
      animateCount('userCount', currentCount, liveUsers, 2000);
    } catch (error) {
      console.error('Error fetching live user count:', error);
      // Optionally, you can display a static number or hide the counter on error
    }
  };

  fetchAndAnimateUsers(); // Initial fetch
  setInterval(fetchAndAnimateUsers, 5000); // Fetch every 5 seconds
}

function animateCount(elementId, start, end, duration) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const startTime = Date.now();
    const startValue = parseInt(start) || 0;
    const endValue = parseInt(end);
    
    const animate = () => {
        const currentTime = Date.now();
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const currentValue = Math.floor(startValue + (endValue - startValue) * easeOutQuart);
        
        element.textContent = currentValue.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    };
    
    animate();
}

function initializeAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animationDelay = '0s';
                entry.target.style.animationPlayState = 'running';
            }
        });
    }, observerOptions);

    document.querySelectorAll('.feature-card, .dashboard-card, .action-card').forEach(el => {
        el.style.animationPlayState = 'paused';
        observer.observe(el);
    });
}

function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                submitBtn.disabled = true;
            }
        });
    });
}

function initializeSkillTags() {
    document.querySelectorAll('.skill-tag').forEach(tag => {
        tag.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.05)';
        });
        
        tag.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

function initializeParallax() {
    const shapes = document.querySelectorAll('.shape');
    
    document.addEventListener('mousemove', function(e) {
        const mouseX = e.clientX / window.innerWidth;
        const mouseY = e.clientY / window.innerHeight;
        
        shapes.forEach((shape, index) => {
            const speed = (index + 1) * 0.02;
            const x = mouseX * speed * 50;
            const y = mouseY * speed * 50;
            
            shape.style.transform = `translate(${x}px, ${y}px)`;
        });
    });
}

window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.background = 'rgba(255,255,255,0.98)';
        navbar.style.backdropFilter = 'blur(20px)';
        navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.15)';
    } else {
        navbar.style.background = 'rgba(255,255,255,0.95)';
        navbar.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
    }
});

function showAlert(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} position-fixed`;
    notification.style.cssText = `
        top: 80px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        animation: slideInRight 0.3s ease-out;
    `;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.remove(), 5000);
}

const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes confettiFall {
        0% { transform: translateY(-10px) rotate(0deg); opacity: 1; }
        100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
    }
    
    .skill-tag.hot::after {
        content: '🔥';
        margin-left: 5px;
    }
    
    .skill-tag.trending::after {
        content: '📈';
        margin-left: 5px;
    }
    
    .skill-tag.popular::after {
        content: '⭐';
        margin-left: 5px;
    }
    
    .live-counter {
        position: relative;
    }
    
    .live-counter::after {
        content: '🔴';
        position: absolute;
        top: -5px;
        right: -15px;
        font-size: 0.8rem;
        animation: blink 2s infinite;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.3; }
    }
`;
document.head.appendChild(style);
