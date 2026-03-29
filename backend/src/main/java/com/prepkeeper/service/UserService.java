package com.prepkeeper.service;

import com.prepkeeper.dto.response.UserResponse;
import com.prepkeeper.entity.User;
import com.prepkeeper.exception.BusinessException;
import com.prepkeeper.exception.ErrorCode;
import com.prepkeeper.repository.CheckinRepository;
import com.prepkeeper.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final CheckinRepository checkinRepository;

    @Transactional(readOnly = true)
    public UserResponse getUserById(String userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));
        return toUserResponse(user);
    }

    @Transactional
    public UserResponse updateUser(String userId, String nickname, String avatarUrl) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        if (nickname != null && !nickname.equals(user.getNickname())) {
            if (userRepository.existsByNickname(nickname)) {
                throw new BusinessException(ErrorCode.NICKNAME_EXISTS);
            }
            user.setNickname(nickname);
        }

        if (avatarUrl != null) {
            user.setAvatarUrl(avatarUrl);
        }

        user = userRepository.save(user);
        return toUserResponse(user);
    }

    @Transactional
    public void updateStreak(String userId, boolean checkedYesterday) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        if (checkedYesterday) {
            // 连续打卡
            user.setCurrentStreak(user.getCurrentStreak() + 1);
            if (user.getCurrentStreak() > user.getMaxStreak()) {
                user.setMaxStreak(user.getCurrentStreak());
            }
        } else {
            // 中断连续
            user.setCurrentStreak(1);
        }

        user.setTotalCheckins(user.getTotalCheckins() + 1);
        userRepository.save(user);
    }

    @Transactional
    public void resetStreak(String userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));
        user.setCurrentStreak(0);
        userRepository.save(user);
    }

    private UserResponse toUserResponse(User user) {
        return UserResponse.builder()
                .userId(user.getUserId())
                .nickname(user.getNickname())
                .email(user.getEmail())
                .avatarUrl(user.getAvatarUrl())
                .totalCheckins(user.getTotalCheckins())
                .currentStreak(user.getCurrentStreak())
                .maxStreak(user.getMaxStreak())
                .createdAt(user.getCreatedAt())
                .build();
    }
}