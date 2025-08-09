package com.codenjoy.dojo.service.chain.transformer;

import com.codenjoy.dojo.enums.TransformerType;
import com.codenjoy.dojo.service.chain.ChainContext;
import com.codenjoy.dojo.service.chain.factory.ServicesProvider;
import com.codenjoy.dojo.service.chain.pojo.TransformerProperties;
import com.codenjoy.dojo.utils.JsonUtils;
import com.codenjoy.dojo.utils.csv.JsonToCsv;

import java.util.List;
import java.util.Map;

import static com.codenjoy.dojo.enums.TransformerType.JSON_CONVERT_TRANSFORMER;
import static com.codenjoy.dojo.utils.csv.Matrix.SEPARATOR;
import static org.apache.commons.lang3.StringUtils.isBlank;

public class JsonConvertTransformer extends BaseTransformer {

    public JsonConvertTransformer(TransformerProperties properties, ServicesProvider services) {
        super(properties, services);
    }

    @Override
    public TransformerType type() {
        return JSON_CONVERT_TRANSFORMER;
    }

    @Override
    public String markdown() {
        return """
                Transformer converts json to `CSV` or `Markdown` format.
                
                Example of configuration:
                ```
                [TRANSFORMER]
                name: CONVERT_JSON
                type: JSON_CONVERT_TRANSFORMER
                input_keys: input_json
                output_key: output
                save_as: true
                template: |
                  {
                    "columnDelimiter": ",",
                    "cellLeftDelimiter": "\"",
                    "cellRightDelimiter": "\"",
                    "lineCharsNeedToBeEscapedWithCellDelimiter": "
                ",
                    "headerDelimiter": null,
                    "lineReplacements": [">""],
                    "paddingToMaxCellLength": false,
                    "removeHeadersDuplicates": true
                  }
                ```
                
                In this example we have a transformer with type `JSON_CONVERT_TRANSFORMER` that has:
                - name `CONVERT_JSON`. This name is used in chain configuration.
                - input parameter: `input_json` - json string where we need to convert values.
                - output parameter: `output` - this is converted output string.
                - save_as: true - this is used to save the output as a Value (false for Documents).
                - template with json settings:
                  - `format` - format of the output string. Can be `csv` or `markdown`. In this case
                    other settings will be ignored.
                  - `columnDelimiter` - delimiter between columns in the output string.
                  - `headerDelimiter` - delimiter between headers in the output string.
                  - `cellLeftDelimiter` - left delimiter for cell values.
                  - `cellRightDelimiter` - right delimiter for cell values.
                  - `lineCharsNeedToBeEscapedWithCellDelimiter` - if any of these characters
                    are present in the line, it will be escaped with cell delimiter.
                  - `lineReplacements` - list of strings that will be replaced in the line. Each string
                """ +
                "    contains the string to be replaced and the replacement string separated by `" + SEPARATOR +"`.\n" +
                """
                  - `paddingToMaxCellLength` - if true, all cells will be padded to the maximum cell length.
                  - `removeHeadersDuplicates` - if true, all duplicate headers will be removed.
                """;
    }

    private String getJson() {
        return inputKey(0);
    }

    @Override
    void innerCall(ChainContext context) {
        String json = context.getValue(getJson());
        String template = template();
        log("Settings is '%s'", template);
        Map<String, Object> object = (Map) JsonUtils.parse(template);

        boolean saveAsValue = parseBoolean("SaveAs", saveAs(), true);
        log("SaveAs is '%s' - save as %s", saveAsValue, saveAsValue ? "Value" : "Documents");

        String result;
        String format = (String) object.get("format");
        if (!isBlank(format)) {
            if (format.equalsIgnoreCase("markdown")) {
                result = JsonToCsv.jsonToMarkdown(json);
            } else if (format.equalsIgnoreCase("csv")) {
                result = JsonToCsv.jsonToCsv(json);
            } else {
                throw new IllegalArgumentException("Unknown format: " + format);
            }
        } else {
                result = JsonToCsv.jsonToCsv(json,
                        (String) object.get("columnDelimiter"),
                        (String) object.get("cellLeftDelimiter"),
                        (String) object.get("cellRightDelimiter"),
                        (String) object.get("lineCharsNeedToBeEscapedWithCellDelimiter"),
                        (String) object.get("headerDelimiter"),
                        (List<String>) object.get("lineReplacements"),
                        (Boolean) object.get("paddingToMaxCellLength"),
                        (Boolean) object.get("removeHeadersDuplicates"));
        }

        setOutput(context, List.of(result), saveAsValue);
    }
}