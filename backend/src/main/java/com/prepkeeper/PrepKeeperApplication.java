package com.prepkeeper;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class PrepKeeperApplication {

    public static void main(String[] args) {
        SpringApplication.run(PrepKeeperApplication.class, args);
    }
}