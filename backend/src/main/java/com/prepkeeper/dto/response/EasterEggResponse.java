package com.prepkeeper.dto.response;

import lombok.Builder;
import lombok.Data;
import java.time.LocalDate;

@Data
@Builder
public class EasterEggResponse {

    private String eggType;
    private String content;
    private LocalDate triggerDate;
}