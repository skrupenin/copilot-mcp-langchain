package com.codenjoy.dojo.utils.csv;

import com.codenjoy.dojo.utils.JsonUtils;
import lombok.SneakyThrows;

import java.util.List;
import java.util.Map;

import static com.codenjoy.dojo.utils.JsonUtils.SORT_KEYS;
import static com.codenjoy.dojo.utils.csv.Matrix.SEPARATOR;

public class JsonToCsv {

    private static final boolean DEBUG = false;

    public static String jsonToCsv(String json) {
        return jsonToCsv(json,
                ",",
                "\"",
                "\"",
                "\n\",",
                null,
                List.of("\"" + SEPARATOR + "\"\""),
                false,
                true);
    }

    public static String jsonToMarkdown(String json) {
        return jsonToCsv(json,
                "|",
                null,
                null,
                null,
                "-",
                null,
                true,
                true);
    }

    @SneakyThrows
    public static String jsonToCsv(
            String json,
            String columnDelimiter,
            String cellLeftDelimiter,
            String cellRightDelimiter,
            String lineCharsNeedToBeEscapedWithCellDelimiter,
            String headerDelimiter,
            List<String> lineReplacements,
            boolean paddingToMaxCellLength,
            boolean removeHeadersDuplicates
    ) {
        List<Object> data = JsonUtils.jsonMapper(!SORT_KEYS).readValue(json, List.class);

        Matrix matrix = new Matrix();

        processElement(matrix, data, "", false, 0);

        if (removeHeadersDuplicates) {
            matrix.removeHeadersDuplicates();
        }
        return matrix.toString(
                columnDelimiter,
                cellLeftDelimiter,
                cellRightDelimiter,
                lineCharsNeedToBeEscapedWithCellDelimiter,
                headerDelimiter,
                lineReplacements,
                paddingToMaxCellLength);
    }

    private static void processElement(Matrix matrix, Object obj, String prefix, boolean sameLine, int depth) {
        int x = 0;
        if (!prefix.isEmpty()) {
            x = matrix.getOrCreateHeader(prefix);
        }
        if (obj instanceof Map) {
            Map<String, Object> map = (Map<String, Object>) obj;
            if (depth > 1) {
                matrix.childHeader();
            }
            for (Map.Entry<String, Object> entry : map.entrySet()) {
                String key = prefix.isEmpty() ? entry.getKey() : prefix + "." + entry.getKey();
                Object value = entry.getValue();
                processElement(matrix, value, key, sameLine, depth + 1);
                sameLine = true;
            }
            if (depth > 1) {
                matrix.parentHeader();
            }
        } else if (obj instanceof List) {
            List<Object> list = (List<Object>) obj;
            for (int y = 0; y < list.size(); y++) {
                if (depth == 0) {
                    matrix.newLine();
                } else {
                    sameLine = y == 0;
                }
                Object item = list.get(y);
                processElement(matrix, item, prefix, sameLine, depth + 1);
            }
        } else {
            matrix.inject(x, sameLine, String.valueOf(obj));
            if (DEBUG) {
                System.out.println("Injecting: " + prefix + " -> " + obj);
                System.out.println("===============================================================================");
                System.out.println(matrix.toString("|", null, null, null, "-", null, true));
                System.out.println("===============================================================================");
            }
        }
    }
}
