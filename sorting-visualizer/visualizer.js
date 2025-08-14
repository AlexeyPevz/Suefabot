class Visualizer {
    constructor(containerId, speedControl) {
        this.container = document.getElementById(containerId);
        this.speedControl = speedControl;
        this.bars = [];
        this.array = [];
    }

    // Инициализация визуализации с массивом
    init(array) {
        this.array = [...array];
        this.container.innerHTML = '';
        this.bars = [];

        const maxValue = Math.max(...array);
        const containerWidth = this.container.offsetWidth;
        const barWidth = Math.max(1, Math.floor(containerWidth / array.length) - 2);

        array.forEach((value, index) => {
            const bar = document.createElement('div');
            bar.className = 'bar';
            bar.style.height = `${(value / maxValue) * 100}%`;
            bar.style.width = `${barWidth}px`;
            bar.dataset.value = value;
            bar.dataset.index = index;
            
            this.container.appendChild(bar);
            this.bars.push(bar);
        });
    }

    // Получить задержку анимации на основе скорости
    getDelay() {
        const speed = parseInt(this.speedControl.value);
        return Math.max(10, 1000 - (speed * 10));
    }

    // Анимация сравнения двух элементов
    async compare(i, j) {
        if (i < 0 || j < 0 || i >= this.bars.length || j >= this.bars.length) return;

        this.bars[i].classList.add('comparing');
        this.bars[j].classList.add('comparing');

        await this.delay();

        this.bars[i].classList.remove('comparing');
        this.bars[j].classList.remove('comparing');
    }

    // Анимация обмена двух элементов
    async swap(i, j) {
        if (i < 0 || j < 0 || i >= this.bars.length || j >= this.bars.length) return;

        this.bars[i].classList.add('swapping');
        this.bars[j].classList.add('swapping');

        await this.delay();

        // Обмениваем высоты столбцов
        const tempHeight = this.bars[i].style.height;
        const tempValue = this.bars[i].dataset.value;

        this.bars[i].style.height = this.bars[j].style.height;
        this.bars[i].dataset.value = this.bars[j].dataset.value;

        this.bars[j].style.height = tempHeight;
        this.bars[j].dataset.value = tempValue;

        await this.delay();

        this.bars[i].classList.remove('swapping');
        this.bars[j].classList.remove('swapping');
    }

    // Обновление значения элемента (для merge sort)
    async update(index, value) {
        if (index < 0 || index >= this.bars.length) return;

        const maxValue = Math.max(...this.array);
        this.bars[index].classList.add('swapping');
        
        await this.delay();
        
        this.bars[index].style.height = `${(value / maxValue) * 100}%`;
        this.bars[index].dataset.value = value;
        
        await this.delay();
        
        this.bars[index].classList.remove('swapping');
    }

    // Пометить элемент как отсортированный
    async markSorted(index) {
        if (index < 0 || index >= this.bars.length) return;
        
        this.bars[index].classList.add('sorted');
        await this.delay(50);
    }

    // Пометить элемент как pivot (для quick sort)
    async markPivot(index) {
        if (index < 0 || index >= this.bars.length) return;
        
        this.bars[index].classList.add('pivot');
    }

    // Убрать метку pivot
    async unmarkPivot(index) {
        if (index < 0 || index >= this.bars.length) return;
        
        this.bars[index].classList.remove('pivot');
    }

    // Сбросить все стили
    reset() {
        this.bars.forEach(bar => {
            bar.classList.remove('comparing', 'swapping', 'sorted', 'pivot');
        });
    }

    // Задержка для анимации
    delay(customDelay = null) {
        const delayTime = customDelay || this.getDelay();
        return new Promise(resolve => setTimeout(resolve, delayTime));
    }

    // Анимация завершения сортировки
    async celebrateCompletion() {
        // Волна зеленого цвета по всем элементам
        for (let i = 0; i < this.bars.length; i++) {
            this.bars[i].classList.add('sorted');
            await this.delay(20);
        }

        // Мигание всех элементов
        await this.delay(300);
        this.bars.forEach(bar => bar.style.transition = 'all 0.3s ease');
        
        for (let i = 0; i < 3; i++) {
            this.bars.forEach(bar => bar.style.transform = 'scaleY(1.1)');
            await this.delay(200);
            this.bars.forEach(bar => bar.style.transform = 'scaleY(1)');
            await this.delay(200);
        }

        this.bars.forEach(bar => bar.style.transition = '');
    }
}