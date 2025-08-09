package com.codenjoy.dojo.utils.csv;

public class Range {

    private int min;
    private int max;

    public Range(int min, int max) {
        this.min = min;
        this.max = max;
    }

    public int min() {
        return min;
    }

    public int max() {
        return max;
    }

    public void next() {
        min = max + 1;
        max = min;
    }

    public void min(int value) {
        min = value;
    }

    public void max(int value) {
        max = value;
    }

    public Range copy() {
        return new Range(min, max);
    }

    @Override
    public String toString() {
        return "[" +
                min +
                "-" + max + ']';
    }
}
