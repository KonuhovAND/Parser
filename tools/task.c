#include <stdio.h>
#include <stdlib.h>
#include <locale.h>

// Функция для вывода матрицы
void printMatrix(int n, float matrix[20][20]) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            printf("%.0f ", matrix[i][j]);
        }
        printf("\n");
    }
}

// Функция для ввода матрицы с защитой от ошибок
int inputMatrix(int n, float matrix[20][20]) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (scanf("%f", &matrix[i][j]) != 1) {
                printf("Ошибка: некорректный ввод\n");
                while (getchar() != '\n');
                return 0;
            }
        }
    }
    return 1;
}

// Функция для нахождения максимума в треугольной области (вариант 3)
// Треугольник расширяется ВПРАВО, захватывая элементы сверху и снизу
float findMaxInTriangle(int n, float matrix[20][20], int i, int j) {
    float max_val = matrix[i][j];
    
    // Идем по столбцам вправо от j
    for (int col = j; col < n; col++) {
        // Расстояние от начального столбца
        int dist = col - j;
        
        // На столбце col проверяем строки от (i - dist) до (i + dist)
        int row_start = i - dist;
        int row_end = i + dist;
        
        // Проверяем границы матрицы
        if (row_start < 0) {
            row_start = 0;
        }
        if (row_end >= n) {
            row_end = n - 1;
        }
        
        // Ищем максимум в диапазоне строк на этом столбце
        for (int row = row_start; row <= row_end; row++) {
            if (matrix[row][col] > max_val) {
                max_val = matrix[row][col];
            }
        }
    }
    
    return max_val;
}

// Функция для построения результирующей матрицы
void buildResultMatrix(int n, float A[20][20], float B[20][20]) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            B[i][j] = findMaxInTriangle(n, A, i, j);
        }
    }
}

int main() {
    setlocale(LC_ALL, "Russian");
    
    int n;
    printf("Введите размер квадратной матрицы (макс. 20): ");
    
    if (scanf("%d", &n) != 1 || n <= 0 || n > 20) {
        printf("Ошибка: размер должен быть числом от 1 до 20\n");
        return 1;
    }
    
    // Очистка буфера ввода
    while (getchar() != '\n');
    
    // Объявление матриц
    float A[20][20];
    float B[20][20];
    
    printf("Введите элементы матрицы A (%d x %d):\n", n, n);
    if (!inputMatrix(n, A)) {
        return 1;
    }
    
    // Вычисляем результирующую матрицу
    buildResultMatrix(n, A, B);
    
    printf("\nМАТРИЦА A (исходная):\n");
    printMatrix(n, A);
    
    printf("\nМАТРИЦА B (результат - максимум в треугольнике):\n");
    printMatrix(n, B);
    
    return 0;
}
