(function () {
    var canvas = document.getElementById('particles');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    var particlesArray;

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resizeCanvas();

    function Particle(x, y, directionX, directionY, size, color) {
        this.x = x;
        this.y = y;
        this.directionX = directionX;
        this.directionY = directionY;
        this.size = size;
        this.color = color;
    }

    Particle.prototype.draw = function () {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2, false);
        ctx.fillStyle = '#FF6B00';
        ctx.fill();
    };

    Particle.prototype.update = function () {
        if (this.x > canvas.width || this.x < 0) {
            this.directionX = -this.directionX;
        }
        if (this.y > canvas.height || this.y < 0) {
            this.directionY = -this.directionY;
        }
        this.x += this.directionX;
        this.y += this.directionY;
        this.draw();
    };

    function init() {
        particlesArray = [];
        var numberOfParticles = (canvas.height * canvas.width) / 15000;
        for (var i = 0; i < numberOfParticles; i++) {
            var size = (Math.random() * 2) + 1;
            var x = (Math.random() * ((innerWidth - size * 2) - (size * 2)) + size * 2);
            var y = (Math.random() * ((innerHeight - size * 2) - (size * 2)) + size * 2);
            var directionX = (Math.random() * 1) - 0.5;
            var directionY = (Math.random() * 1) - 0.5;
            particlesArray.push(new Particle(x, y, directionX, directionY, size, '#FF6B00'));
        }
    }

    function animate() {
        requestAnimationFrame(animate);
        ctx.clearRect(0, 0, innerWidth, innerHeight);
        for (var i = 0; i < particlesArray.length; i++) {
            particlesArray[i].update();
        }
    }

    window.addEventListener('resize', function () {
        resizeCanvas();
        init();
    });

    init();
    animate();
})();
