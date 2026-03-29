package com.prepkeeper.service;

import com.prepkeeper.dto.request.LoginRequest;
import com.prepkeeper.dto.request.RegisterRequest;
import com.prepkeeper.dto.response.AuthResponse;
import com.prepkeeper.dto.response.UserResponse;
import com.prepkeeper.entity.User;
import com.prepkeeper.exception.BusinessException;
import com.prepkeeper.exception.ErrorCode;
import com.prepkeeper.repository.UserRepository;
import com.prepkeeper.security.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider tokenProvider;

    @Transactional
    public AuthResponse register(RegisterRequest request) {
        // 检查邮箱是否已存在
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new BusinessException(ErrorCode.EMAIL_EXISTS);
        }

        // 检查昵称是否已存在
        if (userRepository.existsByNickname(request.getNickname())) {
            throw new BusinessException(ErrorCode.NICKNAME_EXISTS);
        }

        // 创建用户
        User user = new User();
        user.setUserId(cn.hutool.core.util.IdUtil.getSnowflakeNextIdStr());
        user.setEmail(request.getEmail());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setNickname(request.getNickname());
        user.setTotalCheckins(0);
        user.setCurrentStreak(0);
        user.setMaxStreak(0);

        user = userRepository.save(user);

        // 生成Token
        String accessToken = tokenProvider.generateAccessToken(user.getUserId(), user.getEmail());
        String refreshToken = tokenProvider.generateRefreshToken(user.getUserId());

        return AuthResponse.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .tokenType("Bearer")
                .expiresIn(tokenProvider.getExpiration())
                .user(toUserResponse(user))
                .build();
    }

    @Transactional(readOnly = true)
    public AuthResponse login(LoginRequest request) {
        // 查找用户
        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        // 验证密码
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new BusinessException(ErrorCode.PASSWORD_ERROR);
        }

        // 生成Token
        String accessToken = tokenProvider.generateAccessToken(user.getUserId(), user.getEmail());
        String refreshToken = tokenProvider.generateRefreshToken(user.getUserId());

        return AuthResponse.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .tokenType("Bearer")
                .expiresIn(tokenProvider.getExpiration())
                .user(toUserResponse(user))
                .build();
    }

    public AuthResponse refreshToken(String refreshToken) {
        if (!tokenProvider.validateToken(refreshToken)) {
            throw new BusinessException(ErrorCode.TOKEN_INVALID);
        }

        String userId = tokenProvider.getUserIdFromToken(refreshToken);
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        String newAccessToken = tokenProvider.generateAccessToken(user.getUserId(), user.getEmail());
        String newRefreshToken = tokenProvider.generateRefreshToken(user.getUserId());

        return AuthResponse.builder()
                .accessToken(newAccessToken)
                .refreshToken(newRefreshToken)
                .tokenType("Bearer")
                .expiresIn(tokenProvider.getExpiration())
                .user(toUserResponse(user))
                .build();
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