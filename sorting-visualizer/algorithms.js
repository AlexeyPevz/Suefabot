// Класс для отслеживания статистики
class SortingStats {
    constructor() {
        this.comparisons = 0;
        this.swaps = 0;
        this.startTime = 0;
    }

    reset() {
        this.comparisons = 0;
        this.swaps = 0;
        this.startTime = Date.now();
    }

    getElapsedTime() {
        return ((Date.now() - this.startTime) / 1000).toFixed(2);
    }
}

// Базовый класс для алгоритмов сортировки
class SortingAlgorithm {
    constructor(array, visualizer, stats) {
        this.array = array;
        this.visualizer = visualizer;
        this.stats = stats;
        this.isSorting = false;
        this.isPaused = false;
    }

    async compare(i, j) {
        this.stats.comparisons++;
        await this.visualizer.compare(i, j);
        return this.array[i] > this.array[j];
    }

    async swap(i, j) {
        if (i !== j) {
            this.stats.swaps++;
            await this.visualizer.swap(i, j);
            [this.array[i], this.array[j]] = [this.array[j], this.array[i]];
        }
    }

    pause() {
        this.isPaused = true;
    }

    resume() {
        this.isPaused = false;
    }

    stop() {
        this.isSorting = false;
        this.isPaused = false;
    }

    async waitIfPaused() {
        while (this.isPaused && this.isSorting) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    }
}

// Пузырьковая сортировка
class BubbleSort extends SortingAlgorithm {
    async sort() {
        this.isSorting = true;
        const n = this.array.length;

        for (let i = 0; i < n - 1 && this.isSorting; i++) {
            let swapped = false;
            
            for (let j = 0; j < n - i - 1 && this.isSorting; j++) {
                await this.waitIfPaused();
                
                if (await this.compare(j, j + 1)) {
                    await this.swap(j, j + 1);
                    swapped = true;
                }
            }
            
            // Помечаем отсортированный элемент
            await this.visualizer.markSorted(n - i - 1);
            
            if (!swapped) break;
        }
        
        // Помечаем первый элемент как отсортированный
        if (this.isSorting) {
            await this.visualizer.markSorted(0);
        }
    }

    static getDescription() {
        return {
            name: "Пузырьковая сортировка",
            description: "Простой алгоритм, который проходит по массиву несколько раз, сравнивая и меняя местами соседние элементы, если они находятся в неправильном порядке.",
            complexity: {
                best: "O(n)",
                average: "O(n²)",
                worst: "O(n²)",
                space: "O(1)"
            }
        };
    }
}

// Сортировка выбором
class SelectionSort extends SortingAlgorithm {
    async sort() {
        this.isSorting = true;
        const n = this.array.length;

        for (let i = 0; i < n - 1 && this.isSorting; i++) {
            let minIdx = i;
            
            for (let j = i + 1; j < n && this.isSorting; j++) {
                await this.waitIfPaused();
                
                if (await this.compare(minIdx, j)) {
                    minIdx = j;
                }
            }
            
            if (minIdx !== i) {
                await this.swap(i, minIdx);
            }
            
            await this.visualizer.markSorted(i);
        }
        
        if (this.isSorting) {
            await this.visualizer.markSorted(n - 1);
        }
    }

    static getDescription() {
        return {
            name: "Сортировка выбором",
            description: "Алгоритм находит минимальный элемент в неотсортированной части массива и ставит его в начало.",
            complexity: {
                best: "O(n²)",
                average: "O(n²)",
                worst: "O(n²)",
                space: "O(1)"
            }
        };
    }
}

// Сортировка вставками
class InsertionSort extends SortingAlgorithm {
    async sort() {
        this.isSorting = true;
        const n = this.array.length;

        await this.visualizer.markSorted(0);

        for (let i = 1; i < n && this.isSorting; i++) {
            let j = i;
            
            while (j > 0 && this.isSorting) {
                await this.waitIfPaused();
                
                if (await this.compare(j - 1, j)) {
                    await this.swap(j - 1, j);
                    j--;
                } else {
                    break;
                }
            }
            
            await this.visualizer.markSorted(i);
        }
    }

    static getDescription() {
        return {
            name: "Сортировка вставками",
            description: "Алгоритм берет элементы по одному и вставляет их в правильную позицию среди уже отсортированных элементов.",
            complexity: {
                best: "O(n)",
                average: "O(n²)",
                worst: "O(n²)",
                space: "O(1)"
            }
        };
    }
}

// Быстрая сортировка
class QuickSort extends SortingAlgorithm {
    async sort() {
        this.isSorting = true;
        await this.quickSort(0, this.array.length - 1);
        
        // Помечаем все элементы как отсортированные
        if (this.isSorting) {
            for (let i = 0; i < this.array.length; i++) {
                await this.visualizer.markSorted(i);
            }
        }
    }

    async quickSort(low, high) {
        if (low < high && this.isSorting) {
            const pivotIndex = await this.partition(low, high);
            await this.quickSort(low, pivotIndex - 1);
            await this.quickSort(pivotIndex + 1, high);
        }
    }

    async partition(low, high) {
        await this.visualizer.markPivot(high);
        let i = low - 1;

        for (let j = low; j < high && this.isSorting; j++) {
            await this.waitIfPaused();
            
            if (!(await this.compare(j, high))) {
                i++;
                await this.swap(i, j);
            }
        }

        await this.swap(i + 1, high);
        await this.visualizer.unmarkPivot(high);
        return i + 1;
    }

    static getDescription() {
        return {
            name: "Быстрая сортировка",
            description: "Эффективный алгоритм, использующий стратегию 'разделяй и властвуй'. Выбирает опорный элемент и разделяет массив на две части.",
            complexity: {
                best: "O(n log n)",
                average: "O(n log n)",
                worst: "O(n²)",
                space: "O(log n)"
            }
        };
    }
}

// Сортировка слиянием
class MergeSort extends SortingAlgorithm {
    async sort() {
        this.isSorting = true;
        await this.mergeSort(0, this.array.length - 1);
        
        // Помечаем все элементы как отсортированные
        if (this.isSorting) {
            for (let i = 0; i < this.array.length; i++) {
                await this.visualizer.markSorted(i);
            }
        }
    }

    async mergeSort(left, right) {
        if (left < right && this.isSorting) {
            const mid = Math.floor((left + right) / 2);
            await this.mergeSort(left, mid);
            await this.mergeSort(mid + 1, right);
            await this.merge(left, mid, right);
        }
    }

    async merge(left, mid, right) {
        const leftArray = this.array.slice(left, mid + 1);
        const rightArray = this.array.slice(mid + 1, right + 1);
        
        let i = 0, j = 0, k = left;

        while (i < leftArray.length && j < rightArray.length && this.isSorting) {
            await this.waitIfPaused();
            
            this.stats.comparisons++;
            await this.visualizer.compare(left + i, mid + 1 + j);
            
            if (leftArray[i] <= rightArray[j]) {
                this.array[k] = leftArray[i];
                await this.visualizer.update(k, leftArray[i]);
                i++;
            } else {
                this.array[k] = rightArray[j];
                await this.visualizer.update(k, rightArray[j]);
                j++;
            }
            k++;
        }

        while (i < leftArray.length && this.isSorting) {
            await this.waitIfPaused();
            this.array[k] = leftArray[i];
            await this.visualizer.update(k, leftArray[i]);
            i++;
            k++;
        }

        while (j < rightArray.length && this.isSorting) {
            await this.waitIfPaused();
            this.array[k] = rightArray[j];
            await this.visualizer.update(k, rightArray[j]);
            j++;
            k++;
        }
    }

    static getDescription() {
        return {
            name: "Сортировка слиянием",
            description: "Стабильный алгоритм, использующий принцип 'разделяй и властвуй'. Разделяет массив пополам, сортирует части и объединяет их.",
            complexity: {
                best: "O(n log n)",
                average: "O(n log n)",
                worst: "O(n log n)",
                space: "O(n)"
            }
        };
    }
}

// Фабрика для создания алгоритмов
const AlgorithmFactory = {
    bubble: BubbleSort,
    selection: SelectionSort,
    insertion: InsertionSort,
    quick: QuickSort,
    merge: MergeSort
};