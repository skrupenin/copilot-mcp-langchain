package com.codenjoy.dojo.utils.csv;

import org.apache.commons.lang3.tuple.Pair;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Objects;

import static org.apache.commons.lang3.StringUtils.isEmpty;

public class Matrix {

    public static final String EMPTY = null;
    public static final String SEPARATOR = "==>";

    private int currentHeader;
    private int headerSize;
    private int currentLine;
    private int baseLine;
    private List<LinkedList<String>> data;
    private boolean newLine;

    public Matrix() {
        data = new ArrayList<>();
        currentHeader = 0;
        headerSize = 1;
        currentLine = 0;
        baseLine = 0;
        newLine = false;
    }

    public void insertRow(int rowIndex) {
        LinkedList<String> newRow = new LinkedList<>();
        if (data.isEmpty()) {
            data.add(newRow);
            return;
        }
        for (int i = 0; i < data.get(0).size(); i++) {
            newRow.add(EMPTY);
        }
        data.add(rowIndex, newRow);
    }

    public void insertColumn(int colIndex) {
        for (LinkedList<String> row : data) {
            row.add(colIndex, EMPTY);
        }
    }

    public int getOrCreateHeader(String key) {
        if (data.size() <= currentHeader) {
            insertRow(currentHeader);
            currentLine++;
            baseLine++;
        }
        LinkedList<String> header = data.get(currentHeader);
        for (int i = 0; i < header.size(); i++) {
            if (key.equals(header.get(i))) {
                return i;
            }
        }
        if (currentHeader == 0) {
            insertColumn(header.size());
            header.set(header.size() - 1, key);
            return header.size() - 1;
        }

        String parentKey = key.substring(0, key.lastIndexOf("."));

        int parentPos = -1;
        LinkedList<String> parentHeader = data.get(currentHeader - 1);
        for (int i = 0; i < parentHeader.size(); i++) {
            if (Objects.equals(parentHeader.get(i), parentKey)) {
                parentPos = i;
                break;
            }
        }
        if (parentPos == -1) {
            throw new IllegalArgumentException("Parent key not found: " + parentKey);
        }

        if (isEmpty(header.get(parentPos))) {
            header.set(parentPos, key);
            return parentPos;
        }

        int newPos = parentPos;
        String value;
        boolean allChildrenIsEmpty;
        boolean insertBeforeOtherCategory = false;
        do {
            value = header.get(newPos);
            if (value != null && !value.startsWith(parentKey)) {
                insertBeforeOtherCategory = true;
                break;
            }
            allChildrenIsEmpty = checkAllChildrenInHeader(currentHeader + 1, newPos);
            newPos++;
        } while ((!isEmpty(value) || !allChildrenIsEmpty) && newPos < header.size());

        if (!insertBeforeOtherCategory && newPos != header.size()) {
            newPos--;
        }
        insertColumn(newPos);
        header.set(newPos, key);
        return newPos;
    }

    private boolean checkAllChildrenInHeader(int fromY, int x) {
        for (int y = fromY; y < headerSize; y++) {
            LinkedList<String> row = data.get(y);
            if (x < row.size() && !isEmpty(row.get(x))) {
                return false;
            }
        }
        return true;
    }

    public void set(int y, int x, String value) {
        data.get(y).set(x, value);
    }

    public String toString(
            String columnDelimiter,
            String cellLeftDelimiter,
            String cellRightDelimiter,
            String lineCharsNeedToBeEscapedWithCellDelimiter,
            String headerDelimiter,
            List<String> lineReplacements,
            boolean paddingToMaxCellLength
    ) {
        List<Pair<String, String>> replacements = null;
        if (lineReplacements != null) {
            replacements = new ArrayList<>(lineReplacements.size());
            for (String replacement : lineReplacements) {
                String[] parts = replacement.split(SEPARATOR);
                replacements.add(Pair.of(parts[0], parts[1]));
            }
        }
        StringBuilder sb = new StringBuilder();
        int headerDelimiterPos = 0;
        int maxLineLength = 0;
        for (int y = 0; y < data.size(); y++) {
            LinkedList<String> row = data.get(y);
            int lineLength = 0;
            for (int x = 0; x < row.size(); x++) {
                String value = row.get(x);
                value = value == null ? "" : value;

                boolean escape = false;
                if (lineCharsNeedToBeEscapedWithCellDelimiter != null) {
                    escape = containsAny(value, lineCharsNeedToBeEscapedWithCellDelimiter);
                }

                if (replacements != null) {
                    for (Pair<String, String> replacement : replacements) {
                        value = value.replace(replacement.getLeft(), replacement.getRight());
                    }
                }
                if (cellLeftDelimiter != null && escape) {
                    sb.append(cellLeftDelimiter);
                    lineLength += cellLeftDelimiter.length();
                }
                sb.append(value);
                lineLength += value.length();
                if (cellRightDelimiter != null && escape) {
                    sb.append(cellRightDelimiter);
                    lineLength += cellRightDelimiter.length();
                }
                if (paddingToMaxCellLength) {
                    int maxLength = getMaxCellLength(x);
                    int padding = maxLength - value.length();
                    for (int i = 0; i < padding; i++) {
                        sb.append(' ');
                    }
                    lineLength += padding;
                }
                if (x < row.size() - 1) {
                    sb.append(columnDelimiter);
                    lineLength += columnDelimiter.length();
                }
            }
            maxLineLength = Math.max(maxLineLength, lineLength);
            sb.append("\n");
            if (y == headerSize - 1) {
                headerDelimiterPos = sb.length();
            }
        }

        if (headerDelimiter != null) {
            String headerLine = headerDelimiter.repeat(maxLineLength);
            headerLine = headerLine.substring(0, maxLineLength);
            sb.insert(headerDelimiterPos, headerLine + "\n");
        }

        return sb.toString();
    }

    private static boolean containsAny(String value, String chars) {
        for (char c : value.toCharArray()) {
            for (int i = 0; i < chars.length(); i++) {
                if (c == chars.charAt(i)) {
                    return true;
                }
            }
        }
        return false;
    }

    private int getMaxCellLength(int x) {
        int result = 0;
        for (LinkedList<String> row : data) {
            if (x < row.size()) {
                String value = row.get(x);
                result = Math.max(result, value == null ? 0 : value.length());
            }
        }
        return result;
    }

    public void childHeader() {
        currentHeader++;
        if (currentHeader == headerSize) {
            insertRow(headerSize);
            headerSize++;
            baseLine++;
            currentLine++;
        }
    }

    public void parentHeader() {
        currentHeader--;

        if (currentHeader < 0) {
            currentHeader = 0;
        }
    }

    public void inject(int x, boolean sameLine, String value) {
        if (newLine) {
            baseLine = data.size();
            currentLine = baseLine - 1;
            newLine = false;
        }
        if (sameLine) {
            if (data.get(baseLine).get(x) == null) {
                currentLine = baseLine;
            }
        } else {
            currentLine++;
            if (currentLine >= data.size()) {
                insertRow(data.size());
            }
        }
        set(currentLine, x, String.valueOf(value));
    }

    public void removeHeadersDuplicates() {
        for (int y = 0; y < headerSize; y++) {
            LinkedList<String> row = data.get(y);
            for (int x = 0; x < row.size(); x++) {
                String value = row.get(x);
                if (isEmpty(value)) {
                    continue;
                }
                value = value + ".";
                for (int yy = y + 1; yy < headerSize; yy++) {
                    LinkedList<String> nextRow = data.get(yy);
                    for (int xx = 0; xx < row.size(); xx++) {
                        String value2 = nextRow.get(xx);
                        if (value2 == null) {
                            continue;
                        }
                        if (value2.startsWith(value)) {
                            nextRow.set(xx, value2.substring(value.length()));
                        }
                    }
                }
            }
        }
    }

    public void newLine() {
        newLine = true;
    }
}
