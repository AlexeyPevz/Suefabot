// Глобальные переменные
let currentArray = [];
let currentAlgorithm = null;
let stats = new SortingStats();
let visualizer = null;

// DOM элементы
const algorithmSelect = document.getElementById('algorithm-select');
const arraySizeSlider = document.getElementById('array-size');
const sizeValue = document.getElementById('size-value');
const speedControl = document.getElementById('speed-control');
const generateBtn = document.getElementById('generate-btn');
const sortBtn = document.getElementById('sort-btn');
const pauseBtn = document.getElementById('pause-btn');
const resetBtn = document.getElementById('reset-btn');
const comparisonsDisplay = document.getElementById('comparisons');
const swapsDisplay = document.getElementById('swaps');
const timeDisplay = document.getElementById('time');
const algorithmDescription = document.getElementById('algorithm-description');

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    visualizer = new Visualizer('visualization', speedControl);
    generateNewArray();
    updateAlgorithmInfo();
    setupEventListeners();
});

// Генерация нового массива
function generateNewArray() {
    const size = parseInt(arraySizeSlider.value);
    currentArray = Array.from({ length: size }, () => Math.floor(Math.random() * 100) + 1);
    
    visualizer.init(currentArray);
    resetStats();
    enableControls();
}

// Настройка обработчиков событий
function setupEventListeners() {
    arraySizeSlider.addEventListener('input', (e) => {
        sizeValue.textContent = e.target.value;
        generateNewArray();
    });

    generateBtn.addEventListener('click', generateNewArray);

    algorithmSelect.addEventListener('change', () => {
        updateAlgorithmInfo();
        if (currentAlgorithm) {
            currentAlgorithm.stop();
        }
    });

    sortBtn.addEventListener('click', startSorting);
    pauseBtn.addEventListener('click', togglePause);
    resetBtn.addEventListener('click', resetVisualization);
}

// Начать сортировку
async function startSorting() {
    if (currentAlgorithm && currentAlgorithm.isSorting) return;

    disableControls();
    visualizer.reset();
    stats.reset();

    const algorithmType = algorithmSelect.value;
    const AlgorithmClass = AlgorithmFactory[algorithmType];
    
    currentAlgorithm = new AlgorithmClass([...currentArray], visualizer, stats);
    
    updateStatsDisplay();
    const statsInterval = setInterval(updateStatsDisplay, 100);

    try {
        await currentAlgorithm.sort();
        
        if (currentAlgorithm.isSorting) {
            await visualizer.celebrateCompletion();
        }
    } catch (error) {
        console.error('Ошибка сортировки:', error);
    } finally {
        clearInterval(statsInterval);
        updateStatsDisplay();
        enableControls();
    }
}

// Переключение паузы
function togglePause() {
    if (!currentAlgorithm) return;

    if (currentAlgorithm.isPaused) {
        currentAlgorithm.resume();
        pauseBtn.textContent = 'Пауза';
    } else {
        currentAlgorithm.pause();
        pauseBtn.textContent = 'Продолжить';
    }
}

// Сброс визуализации
function resetVisualization() {
    if (currentAlgorithm) {
        currentAlgorithm.stop();
    }
    
    visualizer.init(currentArray);
    resetStats();
    enableControls();
}

// Обновление информации об алгоритме
function updateAlgorithmInfo() {
    const algorithmType = algorithmSelect.value;
    const AlgorithmClass = AlgorithmFactory[algorithmType];
    const description = AlgorithmClass.getDescription();

    algorithmDescription.innerHTML = `
        <p>${description.description}</p>
        <div class="complexity">
            <p><strong>Временная сложность:</strong></p>
            <p>• Лучший случай: ${description.complexity.best}</p>
            <p>• Средний случай: ${description.complexity.average}</p>
            <p>• Худший случай: ${description.complexity.worst}</p>
            <p><strong>Пространственная сложность:</strong> ${description.complexity.space}</p>
        </div>
    `;
}

// Обновление отображения статистики
function updateStatsDisplay() {
    comparisonsDisplay.textContent = stats.comparisons;
    swapsDisplay.textContent = stats.swaps;
    timeDisplay.textContent = stats.getElapsedTime() + 's';
}

// Сброс статистики
function resetStats() {
    stats.reset();
    updateStatsDisplay();
}

// Управление состоянием кнопок
function disableControls() {
    algorithmSelect.disabled = true;
    arraySizeSlider.disabled = true;
    generateBtn.disabled = true;
    sortBtn.disabled = true;
    pauseBtn.disabled = false;
    resetBtn.disabled = false;
}

function enableControls() {
    algorithmSelect.disabled = false;
    arraySizeSlider.disabled = false;
    generateBtn.disabled = false;
    sortBtn.disabled = false;
    pauseBtn.disabled = true;
    resetBtn.disabled = false;
    pauseBtn.textContent = 'Пауза';
}

// Добавление клавиатурных сокращений
document.addEventListener('keydown', (e) => {
    if (e.key === ' ' && !e.target.matches('input, select, button')) {
        e.preventDefault();
        if (currentAlgorithm && currentAlgorithm.isSorting) {
            togglePause();
        } else {
            startSorting();
        }
    } else if (e.key === 'r' && !e.target.matches('input, select, button')) {
        e.preventDefault();
        resetVisualization();
    } else if (e.key === 'g' && !e.target.matches('input, select, button')) {
        e.preventDefault();
        generateNewArray();
    }
});