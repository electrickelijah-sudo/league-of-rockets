using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace RocketLeague
{
    /// <summary>
    /// Animates wheel tire spin based on vehicle linear speed and visual steering angles.
    /// </summary>
    public class WheelRotator : MonoBehaviour
    {
        [Header("=== WHEEL TRANSFORMS ===")]
        public Transform frontLeftWheel;
        public Transform frontRightWheel;
        public Transform rearLeftWheel;
        public Transform rearRightWheel;

        [Header("=== STEERING HUBS ===")]
        public Transform frontLeftHub;
        public Transform frontRightHub;

        [Header("=== PARAMETERS ===")]
        public float wheelRadius = 0.4f;
        public float maxSteerAngle = 28f;
        public float steerSmoothSpeed = 16f;

        private CarController _car;
        private Rigidbody _rb;
        private float _currentSteerAngle = 0f;
        private float _spinAngle = 0f;

        private void Awake()
        {
            _car = GetComponent<CarController>();
            _rb = GetComponent<Rigidbody>();
        }

        private void Update()
        {
            if (_rb == null) return;

            // Calculate forward linear velocity relative to vehicle orientation
            float forwardSpeed = Vector3.Dot(_rb.linearVelocity, transform.forward);

            // Angular velocity: w = v / r (in radians/sec) -> convert to degrees/sec
            float angularSpeedDeg = (forwardSpeed / Mathf.Max(0.01f, wheelRadius)) * Mathf.Rad2Deg;
            _spinAngle += angularSpeedDeg * Time.deltaTime;

            // Steering Angle
            float targetSteer = 0f;
            if (_car != null)
            {
                float steerInput = 0f;
                if (_car.isAI)
                {
                    steerInput = _car.aiSteer;
                }
                else
                {
                    if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow)) steerInput += 1f;
                    if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow)) steerInput -= 1f;
                    if (Mathf.Approximately(steerInput, 0f)) steerInput = Input.GetAxis("Horizontal");
                }
                targetSteer = steerInput * maxSteerAngle;
            }

            _currentSteerAngle = Mathf.Lerp(_currentSteerAngle, targetSteer, Time.deltaTime * steerSmoothSpeed);

            // Apply spin to wheels
            Quaternion spinRot = Quaternion.Euler(_spinAngle, 0f, 0f);

            if (rearLeftWheel != null) rearLeftWheel.localRotation = spinRot;
            if (rearRightWheel != null) rearRightWheel.localRotation = spinRot;

            // Front wheels spin and steer
            if (frontLeftHub != null)
            {
                frontLeftHub.localRotation = Quaternion.Euler(0f, _currentSteerAngle, 0f);
                if (frontLeftWheel != null) frontLeftWheel.localRotation = spinRot;
            }
            else if (frontLeftWheel != null)
            {
                frontLeftWheel.localRotation = Quaternion.Euler(_spinAngle, _currentSteerAngle, 0f);
            }

            if (frontRightHub != null)
            {
                frontRightHub.localRotation = Quaternion.Euler(0f, _currentSteerAngle, 0f);
                if (frontRightWheel != null) frontRightWheel.localRotation = spinRot;
            }
            else if (frontRightWheel != null)
            {
                frontRightWheel.localRotation = Quaternion.Euler(_spinAngle, _currentSteerAngle, 0f);
            }
        }
    }
}
